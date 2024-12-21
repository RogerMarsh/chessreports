# resultsdatabase.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using Berkeley DB database via berkeleydb."""

from berkeleydb.db import (
    DB_CREATE,
    DB_RECOVER,
    DB_INIT_MPOOL,
    DB_INIT_LOCK,
    DB_INIT_LOG,
    DB_INIT_TXN,
    DB_PRIVATE,
)

from solentware_base import berkeleydb_database

from ..core.filespec import FileSpec
from ..basecore import database


class ResultsDatabase(database.Database, berkeleydb_database.Database):
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
                DB_CREATE
                | DB_RECOVER
                | DB_INIT_MPOOL
                | DB_INIT_LOCK
                | DB_INIT_LOG
                | DB_INIT_TXN
                | DB_PRIVATE
            ),
        }

        super().__init__(
            dbnames,
            DBfile,
            environment,
            use_specification_items=use_specification_items,
            **kargs,
        )

    def _delete_database_names(self):
        """Override and return tuple of filenames to delete."""
        return (
            self.database_file,
            self.dbenv.get_lg_dir(),
            self.database_file + "-lock",
        )

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
