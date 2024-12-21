# create_chessreports_database.py
# Copyright 2020 Roger Marsh
# Licence: See LICENSE.txt (BSD licence)

"""Create empty database with chosen database engine and segment size."""

from solentware_base.tools import create_database

try:
    from ..unqlite import resultsdatabase as chessunqlite
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessunqlite = None
try:
    from ..vedis import resultsdatabase as chessvedis
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessvedis = None
if create_database._deny_sqlite3:
    chesssqlite3 = None
else:
    try:
        from ..sqlite import resultsdatabase as chesssqlite3
    except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
        chesssqlite3 = None
try:
    from ..apsw import resultsdatabase as chessapsw
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessapsw = None
try:
    from ..db import resultsdatabase as chessdb
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessdb = None
try:
    from ..berkeleydb import resultsdatabase as chessberkeleydb
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessberkeleydb = None
try:
    from ..db_tkinter import resultsdatabase as chessdbtkinter
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessdbtkinter = None
try:
    from ..dpt import resultsdatabase as chessdpt
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessdpt = None
try:
    from ..lmdb import resultsdatabase as chesslmdb
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chesslmdb = None


class CreateChessReportsDatabase(create_database.CreateDatabase):
    """Create a ChessReports database."""

    _START_TEXT = "".join(
        (
            "ChessReports would create a new database with the top-left ",
            "engine, and segment size 4000.",
        )
    )

    def __init__(self):
        """Build the user interface."""
        engines = {}
        if chessunqlite:
            engines[chessunqlite.unqlite_database.unqlite] = (
                chessunqlite.ResultsDatabase
            )
        if chessvedis:
            engines[chessvedis.vedis_database.vedis] = (
                chessvedis.ResultsDatabase
            )
        if chesssqlite3:
            engines[chesssqlite3.sqlite3_database.sqlite3] = (
                chesssqlite3.ResultsDatabase
            )
        if chessapsw:
            engines[chessapsw.apsw_database.apsw] = chessapsw.ResultsDatabase
        if chessdb:
            engines[chessdb.bsddb3_database.bsddb3] = chessdb.ResultsDatabase
        if chesslmdb:
            engines[chesslmdb.lmdb_database.lmdb] = chesslmdb.ResultsDatabase
        if chessberkeleydb:
            engines[chessberkeleydb.berkeleydb_database.berkeleydb] = (
                chessberkeleydb.ResultsDatabase
            )
        if chessdbtkinter:
            engines[chessdbtkinter.db_tkinter_database.db_tcl] = (
                chessdbtkinter.ResultsDatabase
            )
        if chessdpt:
            engines[chessdpt.dpt_database._dpt.dptapi] = (
                chessdpt.ResultsDatabase
            )
        super().__init__(title="Create ChessReports Database", engines=engines)


if __name__ == "__main__":
    CreateChessReportsDatabase().root.mainloop()
