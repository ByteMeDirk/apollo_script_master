import logging
from glob import glob
from hashlib import md5, sha256, sha512
import re
import sqlparse


def minify_sql(sql: str) -> str:
    """
    Minifies SQL statements.

    Args:
        sql: The SQL statement to minify.

    Returns:
        The minified SQL statement.
    """
    logging.info(f"Minifying SQL statement.")
    parsed = sqlparse.parse(sql, encoding="utf8")

    # Remove comments, newlines, and whitespace from the SQL statement using regex.
    statements = []
    for statement in parsed:
        statement = re.sub(r"--.*?\n", " ", str(statement))  # Remove single line comments.
        statement = re.sub(r"\n", " ", str(statement))  # Remove newlines.
        statement = re.sub(r"\s+", " ", str(statement))  # Remove whitespace.
        statement = re.sub(r"\/\*.*?\*\/", " ", str(statement))  # Remove multi-line comments.
        statements.append(statement)

    return "".join(statements).strip()


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
