"""
A SQL class to manage SQL manipulation outside of the ORM.
"""
import re


class SQL:
    """
    Manipulate SQL statements.
    """
    REGEX_MAP = re.compile(
        r'(^)?[^\S\n]*(?:--.*$|/\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )

    def __init__(self, sql: str):
        """
        Args:
            sql: The SQL statement to manipulate.

        """
        self.sql = sql

    def minify(self) -> str:
        """
        Minifies SQL statements.

        Returns:
            The minified SQL statement.
        """
        return self.REGEX_MAP.sub(' ', self.sql).strip()
