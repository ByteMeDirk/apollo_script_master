import logging
import os
import re
import time
from datetime import datetime

from sqlalchemy import Integer, Column, String, DateTime, Boolean, text
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from apollo_script_master.config import validate_config_file
from .file_management import collect_files, hash_file_collection, minify_sql

BASE = declarative_base()
ASP_CONFIG = os.getenv("ASP_CONFIG", {})


def url_manager(**kwargs) -> str:
    """
    Generates a SQL alchemy URL from the kwargs. for the given SQL engine type and driver if applicable.
    URL returned is also url safe.

    Args:
        **kwargs: The keyword arguments to use.

    Returns:
        The URL.
    """
    try:
        if kwargs.get("drivername") == "postgresql":
            return f"{kwargs.get('drivername')}+{kwargs.get('dialect', 'psycopg2')}://{kwargs.get('username')}:{kwargs.get('password')}@{kwargs.get('host')}:{kwargs.get('port', 5432)}/{kwargs.get('database', 'postgres')}"

        raise KeyError(
            f"The provided drivername/dialect is not supported: {kwargs.get('drivername')}/{kwargs.get('dialect')}.")
    except KeyError as error:
        logging.error(f"An error occurred when trying to generate the URL: {error}.")
        raise error


class ASMImpl:
    def __init__(
            self,
            conn_params: dict,
            directory: str,
            author: str,
            config_file: str = "asm.yml",
    ):
        self.__conn_params = conn_params
        self.directory = directory
        self.author = author
        self.config_file = validate_config_file(config_file)
        self.session = self._set_session()

    def _set_session(self) -> sessionmaker.__call__:
        """
        Sets the ORM session for the ASM object.
        A connection string is generated from the conn_params and passed to the sessionmaker.
        """
        logging.info("Setting up ASM session.")
        url = url_manager(**self.__conn_params)
        engine = create_engine(
            url,
            echo=self.config_file.get("global", {}).get("echo", False),
            isolation_level=self.config_file.get("global", {}).get("isolation_level", "READ UNCOMMITTED"),
        )
        BASE.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        return session()

    def _populate_lock_table(self) -> None:
        logging.info("Populating lock table.")
        try:
            if not self.session.query(ASMDeployLock).count() > 0:
                logging.info("Lock table is empty, populating.")
                record = ASMDeployLock(
                    locked=False,
                    lockedby="root"
                )
                self.session.add(record)
        except SQLAlchemyError as error:
            logging.error(f"An error occurred when trying to populate the lock table: {error}.")
            raise error

    def _generate_filesets(self) -> dict:
        """
        Generate the filesets for the directory.

        Returns:
            The filesets as a dictionary.
        """
        is_recursive = self.config_file.get("checksum", {}).get("recursive", False)
        algorithm = self.config_file.get("checksum", {}).get("algorithm", "md5")
        filesets = {}
        for filepath, filedata in collect_files(filepath=self.directory, recursive=is_recursive):
            for checksum in hash_file_collection(contents=filedata, algorithm=algorithm):
                filesets[filepath] = {
                    "data": minify_sql(filedata),
                    "checksum": checksum,
                    "algorithm": algorithm,
                }
        return filesets

    def _close_lock(self) -> None:
        """
        First check if the lock is open in ASMDeployLock, if not wait until it is.
        Then set the lock to True so that no other process can run.
        Checks:
            deploy_lock_table:
              lock_check_retries
              lock_check_wait
        To determine the wait period and the number of retries.
        """
        logging.info("Closing lock.")
        lock_check_retries = self.config_file.get("deploy_lock_table", {}).get("lock_check_retries", 10)
        lock_check_wait = self.config_file.get("deploy_lock_table", {}).get("lock_check_wait", 30)
        record = self.session.query(ASMDeployLock).first()
        for _ in range(lock_check_retries):
            self.session.refresh(record)
            if record.locked is False:
                record.locked = True
                record.lockedby = self.author
                self.session.add(record)
                self.session.commit()
                break
            else:
                logging.info(
                    f"Lock is already closed, waiting {lock_check_wait} seconds. {_ + 1}/{lock_check_retries}.")
                time.sleep(lock_check_wait)
        else:
            logging.error("Lock is still closed, cannot continue.")
            raise Exception("Lock is still closed, cannot continue.")

    def _open_lock(self) -> None:
        """
        Open the lock in ASMDeployLock.
        """
        logging.info("Opening lock.")
        record = self.session.query(ASMDeployLock).first()
        record.locked = False
        record.lockedby = None
        self.session.add(record)
        self.session.commit()

    def _populate_filesets(self, filesets: dict) -> None:
        """
        Populate the filesets into the database.

        Args:
            filesets: The filesets to populate.

        Returns:
            None
        """
        dry_run = self.config_file.get("global", {}).get("dry_run", False)
        for filepath in filesets:
            record = self.session.query(ASMDeploy).filter(ASMDeploy.filepath == filepath).first()
            if record is None:
                logging.info(f"File {filepath} is not in the table, adding.")
                if not dry_run:
                    record = ASMDeploy(
                        filepath=filepath,
                        data=filesets[filepath].get("data"),
                        checksum=filesets[filepath].get("checksum"),
                        algorithm=filesets[filepath].get("algorithm"),
                        author=self.author,
                    )
                    self.session.add(record)
                    try:
                        self.session.execute(text(record.data))
                    except SQLAlchemyError as error:
                        logging.error(f"An error occurred when trying to execute the script: {error}.")
                        raise error from error
            else:
                logging.info(f"File {filepath} is in the table, checking for changes.")
                if record.checksum != filesets[filepath].get("checksum"):
                    logging.info(f"File {filepath} has changed, updating.")
                    if not dry_run:
                        record.data = filesets[filepath].get("data")
                        record.checksum = filesets[filepath].get("checksum")
                        record.algorithm = filesets[filepath].get("algorithm")
                        record.author = self.author
                        self.session.add(record)
                        try:
                            self.session.execute(text(record.data))
                        except SQLAlchemyError as error:
                            logging.error(f"An error occurred when trying to execute the script: {error}.")
                            raise error from error
                else:
                    logging.info(f"File {filepath} has not changed, skipping.")

    def _delete(self, filesets: dict):
        """
        Checks the paths in the table against the paths in the directory.
        If the path is not in the directory, add it to the deletions table, and remove it from the deploy table.
        Return a list of the sql data that was deleted.
        """
        records = self.session.query(ASMDeploy).all()
        sql_data = []
        for record in records:
            if record.filepath not in filesets:
                # add to sql data
                logging.info(f"File {record.filepath} is not in the directory, deleting.")
                sql_data.append(record)
                self.session.delete(record)

                # add to deletions table
                deletion = ASMDeployDeletions(
                    deploy_id=record.id,
                    filepath=record.filepath,
                    data=record.data,
                    author=self.author,
                )
                self.session.add(deletion)

        return sql_data

    def _execute_deletions(self, deletions: list) -> None:
        """
        Use regex to find the Table, FUnction, Procedure or View and execute the DROP statement.
        """
        pattern = re.compile(r"(CREATE\s+OR\s+REPLACE|CREATE\s+OR\s+ALTER|CREATE|ALTER|REPLACE)\s+(FUNCTION|TABLE|VIEW|PROCEDURE)\s+([\w\.]+)\s*\(")
        for deletion in deletions:
            for match in re.finditer(pattern, deletion.data):
                object_type = match.group(2)
                object_name = match.group(3)
                logging.info(f"Found {object_type} {object_name}, dropping.")
                self.session.execute(text(f"DROP {object_type} {object_name} CASCADE;"))

    def run(self) -> None:
        logging.info("Running ASM session.")
        try:
            self._populate_lock_table()
            self._close_lock()
            filesets = self._generate_filesets()
            self._populate_filesets(filesets=filesets)
            deletions = self._delete(filesets=filesets)
            self._execute_deletions(deletions=deletions)
            self.session.commit()
        except SQLAlchemyError as error:
            logging.error(f"An error occurred within the session: {error}.")
            self.session.rollback()
            raise error from error
        finally:
            logging.info("Closing ASM session.")
            self._open_lock()
            self.session.close()


class ASMDeploy(BASE):
    """
    ASMDeploy is a table to store the md5 checksum of the script and the script itself.
    """

    __tablename__ = ASP_CONFIG.get("deploy_table", {}).get("name", "ASMDeploy")
    __table_args__ = ASP_CONFIG.get("deploy_table", {}).get("args", {})

    id = Column(Integer, primary_key=True)
    filepath = Column(String)
    data = Column(String)
    checksum = Column(String)
    algorithm = Column(String)

    author = Column(String)
    date = Column(DateTime, default=datetime.now())


class ASMDeployLock(BASE):
    """
    ASMDeployLock is a table to store the lock state of the deployment.
    """

    __tablename__ = ASP_CONFIG.get("deploy_lock_table", {}).get("name", "ASMDeployLock")
    __table_args__ = ASP_CONFIG.get("deploy_lock_table", {}).get("args", {})

    id = Column(Integer, primary_key=True)
    locked = Column(Boolean)
    date = Column(DateTime, default=datetime.now())
    lockedby = Column(String)


class ASMDeployDeletions(BASE):
    """
    ASMDeployDeletions is a table to store the deleted objects for reference and backup.
    """

    __tablename__ = ASP_CONFIG.get("deploy_deletions_table", {}).get("name", "ASMDeployDeletions")
    __table_args__ = ASP_CONFIG.get("deploy_deletions_table", {}).get("args", {})

    id = Column(Integer, primary_key=True)
    deploy_id = Column(Integer)
    filepath = Column(String)
    data = Column(String)

    author = Column(String)
    date = Column(DateTime, default=datetime.now())
