# dbasedatarow.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Define a row from a dBaseIII file."""

import tkinter

from solentware_base.core.record import KeydBaseIII, Value, RecorddBaseIII

from solentware_grid.gui.datarow import (
    DataHeader,
    DataRow,
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
)


class DBaseDataHeader(DataHeader):
    """Provide methods to create a new header and configure its widgets."""

    @staticmethod
    def make_header_specification(fieldnames=None):
        """Return dbase file header specification."""
        if fieldnames is None:
            return DBaseDataRow.header_specification
        hs = []
        for col, fn in enumerate(fieldnames):
            hs.append(DBaseDataRow.header_specification[0].copy())
            hs[-1][GRID_CONFIGURE] = {"column": col, "sticky": tkinter.EW}
            hs[-1][WIDGET_CONFIGURE] = {"text": fn}
        return hs


class DBaseDataRow(RecorddBaseIII, DataRow):
    """Provide methods to create, for display, a row from a dBaseIII file."""

    # The header is derived from file so define a null header here
    header_specification = (
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": ""},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1},
            ROW: 0,
        },
    )
    # The row is derived from file so define a null row here
    row_specification = (
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            ROW: 0,
        },
    )

    def __init__(self, database=None):
        """Create a dBaseIII row definition attatched to database."""
        super().__init__(keyclass=KeydBaseIII, valueclass=Value)
        self.set_database(database)
        self.row_specification = []

    def grid_row(self, textitems=(), **kargs):
        """Return tuple of instructions to create row.

        Create row specification from dBase file fieldnames.
        Create textitems argument for DBaseDataRow instance.

        textitems arguments is ignored and is present for compatibility.

        """
        fn = self.database.dbasefiles[self.dbname].dbaseobject.fieldnames
        self.row_specification = self.make_row_specification(fn)
        v = self.value.__dict__
        return super().grid_row(
            textitems=tuple(v.get(f, "") for f in fn), **kargs
        )

    @staticmethod
    def make_row_specification(fieldnames=None):
        """Return dbase file row specification."""
        if fieldnames is None:
            return DBaseDataRow.row_specification
        hs = []
        for col in range(len(fieldnames)):
            hs.append(DBaseDataRow.row_specification[0].copy())
            hs[-1][GRID_CONFIGURE] = {"column": col, "sticky": tkinter.EW}
        return hs
