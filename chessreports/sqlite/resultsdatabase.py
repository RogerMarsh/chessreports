# resultsdatabase.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using Sqlite3 database via sqlite3."""

from solentware_base import sqlite3_database

from ..core.filespec import FileSpec
from ..basecore import database


class ResultsDatabase(database.Database, sqlite3_database.Database):
    """Methods and data structures to create, open, and close database."""

    _knownnames_modulename = "chessreports.basecore.knownnamesds"

    def __init__(
        self,
        sqlite3file,
        use_specification_items=None,
        dpt_records=None,
        **kargs,
    ):
        """Define database specification then delegate."""
        names = FileSpec(
            use_specification_items=use_specification_items,
            dpt_records=dpt_records,
        )

        super().__init__(
            names,
            sqlite3file,
            use_specification_items=use_specification_items,
            **kargs,
        )

    def _delete_database_names(self):
        """Override and return tuple of filenames to delete."""
        return (
            self.database_file,
            self.database_file + "-lock",
            self.database_file + "-journal",
        )
