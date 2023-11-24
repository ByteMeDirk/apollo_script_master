"""
File management module.
"""

import logging
from glob import glob
from hashlib import md5, sha256, sha512

from .sql import SQL


def minify_sql(sql: str) -> str:
    """
    Minifies SQL statements.

    Args:
        sql: The SQL statement to minify.

    Returns:
        The minified SQL statement.
    """
    logging.info("Minifying SQL statement.")
    sql_manager = SQL(sql)
    return sql_manager.minify()


def collect_files(filepath: str, recursive: bool = False) -> tuple:
    """
    Collects files from a given filepath.

    Args:
        filepath: The filepath to collect files from.
        recursive: Whether to recursively collect files.

    Returns:
        A tuple containing the file path and the file contents.
    """
    for file in glob(filepath, recursive=recursive):
        with open(file, "r") as _rfile:
            yield file, _rfile.read()


def hash_file_collection(contents: str, algorithm: str = "md5") -> str:
    """
    Hashes a file collection.

    Args:
        contents: The contents of the file collection.
        algorithm: The algorithm to use.

    Returns:
        A hash of the file collection.
    """
    if algorithm == "sha256":
        yield sha256(contents.encode("utf8")).hexdigest()
    elif algorithm == "md5":
        yield md5(contents.encode("utf8")).hexdigest()
    elif algorithm == "sha512":
        yield sha512(contents.encode("utf8")).hexdigest()
    else:
        raise ValueError(f"Algorithm {algorithm} is not supported.")
