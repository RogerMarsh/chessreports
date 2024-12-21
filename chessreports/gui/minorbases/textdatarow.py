# textdatarow.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Define a row from a text file."""

import tkinter

from solentware_base.core.record import KeyText, ValueText, RecordText

from solentware_grid.gui.datarow import (
    DataHeader,
    DataRow,
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
)


class TextDataHeader(DataHeader):
    """Provide methods to create a new header and configure its widgets."""

    @staticmethod
    def make_header_specification(fieldnames=None):
        """Return dbase file header specification."""
        if fieldnames is None:
            return TextDataRow.header_specification
        hs = []
        for col, fn in enumerate(fieldnames):
            hs.append(TextDataRow.header_specification[0].copy())
            hs[-1][GRID_CONFIGURE] = {"column": col, "sticky": tkinter.EW}
            hs[-1][WIDGET_CONFIGURE] = {"text": fn}
        return hs


class TextDataRow(RecordText, DataRow):
    """Provide methods to display a row of data from a text file."""

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
        """Create a text row definition attatched to database."""
        super().__init__(keyclass=KeyText, valueclass=ValueText)
        self.set_database(database)
        self.row_specification = []

    def grid_row(self, textitems=(), **kargs):
        """Return tuple of instructions to create row.

        Create row specification for text file treating line as one field.
        Create textitems argument for TextDataRow instance.

        textitems arguments is ignored and is present for compatibility.

        """
        r = (self.value.text,)
        self.row_specification = self.make_row_specification(
            list(range(len(r)))
        )
        return super().grid_row(textitems=r, **kargs)

    @staticmethod
    def make_row_specification(fieldnames=None):
        """Return dbase file row specification."""
        if fieldnames is None:
            return TextDataRow.row_specification
        hs = []
        for col in range(len(fieldnames)):
            hs.append(TextDataRow.row_specification[0].copy())
            hs[-1][GRID_CONFIGURE] = {"column": col, "sticky": tkinter.EW}
        return hs
