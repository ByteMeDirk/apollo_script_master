import logging
from urllib.parse import quote_plus
import os
from sqlalchemy import create_engine, URL, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime

from sqlalchemy import Integer, Column, String, DateTime, Boolean, __version__

from apollo_script_master.config import validate_config_file

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

    def run(self) -> None:
        logging.info("Running ASM session.")
        try:
            self._populate_lock_table()
            self.session.commit()
        except SQLAlchemyError as error:
            logging.error(f"An error occurred within the session: {error}.")
            self.session.rollback()
            raise error from error
        finally:
            logging.info("Closing ASM session.")
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
    md5 = Column(String)

    author = Column(String)
    date = Column(DateTime, default=datetime.now())
    version = Column(String, default=__version__)


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

    version = Column(String, default=__version__)


class ASMDeployDeletions(BASE):
    """
    ASMDeployDeletions is a table to store the deleted objects for reference and backup.
    """

    __tablename__ = ASP_CONFIG.get("deploy_deletions_table", {}).get("name", "ASMDeployDeletions")
    __table_args__ = ASP_CONFIG.get("deploy_deletions_table", {}).get("args", {})

    id = Column(Integer, primary_key=True)
    filepath = Column(String)
    data = Column(String)

    author = Column(String)
    date = Column(DateTime, default=datetime.now())
    version = Column(String, default=__version__)
