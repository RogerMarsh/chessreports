# ecfdaterow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display dates of data from ECF."""

import tkinter

from solentware_grid.gui.datarow import (
    DataRow,
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
)

from ...core.ecf.ecfrecord import ECFrefDBrecordECFdate


class ECFrefDBrowECFdate(ECFrefDBrecordECFdate, DataRow):
    """Display an ECF date record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Date", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "etdate"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Data Type", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "ettype"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Action", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "etaction"},
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link ECF master file date record to database."""
        super().__init__()
        self.set_database(database)
        self.row_specification = [
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.CENTER},
                GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.CENTER},
                GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.W},
                GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
                ROW: 0,
            },
        ]

    def grid_row(self, textitems=(), **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for ECFrefDBrowECFdate instance.

        textitems arguments is ignored and is present for compatibility.

        """
        return super().grid_row(
            textitems=(
                self.key.ECFdate,
                self.value.ECFobjtype,
                self.value.ECFtxntype,
            ),
            **kargs
        )
