"""
The apollo_script_master package is a Python package that
can be used to manage SQL scripts in a directory.

The package is designed to be used as a command line tool
and can be called as `apollo_script_master`
or `asm` for short.

The package is designed to be used with a YAML configuration file.
The default configuration file is `asm.yml` and can be defined in the
same directory as the SQL scripts to be managed.
"""
import argparse
import json
import logging
import sys

from apollo_script_master.config import validate_config_file
from ._asm.orm import ASMImpl

__version__ = "0.0.1"
__author__ = f"""
{'#' * 90}#
              _             _ _     ___         _      _   __  __         _           
             /_\\  _ __  ___| | |___/ __| __ _ _(_)_ __| |_|  \\/  |__ _ __| |_ ___ _ _ 
            / _ \\| '_ \\/ _ \\ | / _ \\__ \\/ _| '_| | '_ \\  _| |\\/| / _` (_-<  _/ -_) '_|
Welcome to /_/ \\_\\ .__/\\___/_|_\\___/___/\\__|_| |_| .__/\\__|_|  |_\\__,_/__/\\__\\___|_|  !
                 |_|                             |_|                                  
{'#' * (87 - len(__version__))} v.{__version__}# """

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ASM(ASMImpl):
    """
    The ASM class to manage the ASM process.
    """

    def __init__(
            self,
            conn_params: dict,
            directory: str,
            author: str,
            config_file: str = "asm.yml",
    ):
        super().__init__(conn_params, directory, author, config_file)


def main():
    """
    The main function to start the process.

    To call apollo_script_master from the command line, use the following:
    >>> python -m apollo_script_master --conn_params  -directory --author

    The conn_params argument is a JSON string containing the connection parameters to use for the connection.
    For example:
    >>> {"engine": "mssql", "host": "localhost", "port": 1433, "database": "master", "username": "sa", "password": "password"}
    """
    logging.info(__author__)
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument("--conn_params", type=str, help="The connection parameters to use for the connection.", )
        parser.add_argument("--directory", type=str, help="The directory of SQL files to be managed.")
        parser.add_argument("--author", type=str, help="The author to use for the connection.")
        args = parser.parse_args()

        asm = ASM(
            conn_params=json.loads(args.conn_params),
            directory=args.directory,
            author=args.author
        )
        asm.run()
    except Exception as error:
        logging.error(f"An error occurred when trying to start the process: {error}.")
        sys.exit(1)


if __name__ == "__main__":
    main()
