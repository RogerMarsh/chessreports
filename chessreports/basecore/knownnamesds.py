# knownnamesds.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide a datasource cursor for the recordset from KnownNames class.

The KnownNamesDS class in this module supports the apsw, db, and sqlite3,
intefaces to a database.

See the ..dpt.knownnames module for the KnownNamesDS class for DPT.

"""

from solentware_grid.core.datasourcecursor import DataSourceCursor

from .knownnames import KnownNames


class KnownNamesDS(DataSourceCursor, KnownNames):
    """Extend KnownNmaes with a DataSourceCursor."""
