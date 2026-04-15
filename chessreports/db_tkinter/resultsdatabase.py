# resultsdatabase.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using Berkeley DB database via tkinter Tcl API."""

import os

from solentware_base import db_tkinter_database

from ..core.filespec import FileSpec
from ..basecore import database


class ResultsDatabase(database.Database, db_tkinter_database.Database):
    """Methods and data structures to create, open, and close database."""

    _knownnames_modulename = "chessreports.basecore.knownnamesds"

    def __init__(
        self,
        DBfile,
        use_specification_items=None,
        dpt_records=None,
        **kargs,
    ):
        """Define database specification and environment then delegate."""
        dbnames = FileSpec(
            use_specification_items=use_specification_items,
            dpt_records=dpt_records,
        )

        environment = {
            "flags": (
                "-create",
                "-recover",
                "-txn",
                "-private",
                "-system_mem",
            ),
        }

        super().__init__(
            dbnames,
            folder=DBfile,
            environment=environment,
            use_specification_items=use_specification_items,
            **kargs,
        )

    def delete_database(self):
        """Close and delete the open chess results database."""
        return super().delete_database(
            (self.database_file, self._get_log_dir_name())
        )

    # Not clear why _keyify is necessary or just returns value for Berkeley DB.
    def _keyify(self, value):
        """Tranform a value from an ECF DbaseIII file for database key search.

        Overrides the default in database.Database which decodes value.

        """
        return value

    # Not clear why _keybyteify is necessary except it is same as for _keyify.
    # See version in db.resultsdatabase.
    def _keybyteify(self, value):
        """Tranform a value from an ECF json download for database key search.

        Overrides the default in database.Database which returns value.

        """
        return value.encode("iso-8859-1")
