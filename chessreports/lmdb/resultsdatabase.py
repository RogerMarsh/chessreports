# resultsdatabase.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using Symas LMMD database via lmdb."""

from solentware_base import lmdb_database

from ..core.filespec import FileSpec
from ..basecore import database


class ResultsDatabase(database.Database, lmdb_database.Database):
    """Methods and data structures to create, open, and close database."""

    _knownnames_modulename = "chessreports.basecore.knownnamesds"

    def __init__(
        self,
        DBfile,
        use_specification_items=None,
        dpt_records=None,
        **kargs,
    ):
        """Define database specification then delegate."""
        dbnames = FileSpec(
            use_specification_items=use_specification_items,
            dpt_records=dpt_records,
        )

        super().__init__(
            dbnames,
            DBfile,
            use_specification_items=use_specification_items,
            **kargs,
        )

    def _delete_database_names(self):
        """Override and return tuple of filenames to delete."""
        return (self.database_file, self.database_file + "-lock")

    # Not clear why keyify is necessary or just returns value for Berkeley DB.
    def keyify(self, value):
        """Tranform a value from an ECF DbaseIII file for database key search.

        Overrides the default in database.Database which decodes value.

        """
        return value

    # Not clear why keybyteify is necessary except it is same as for keyify.
    # See version in db.resultsdatabase.
    def keybyteify(self, value):
        """Tranform a value from an ECF json download for database key search.

        Overrides the default in database.Database which returns value.

        """
        return value.encode("iso-8859-1")
