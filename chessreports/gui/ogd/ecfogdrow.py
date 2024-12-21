# ecfogdrow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display ECF player details from Online Grading List."""

import tkinter

from solentware_grid.gui.datarow import (
    DataRow,
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
)

from ...core.ogd import ecfogdrecord


class ECFrefOGDrowPlayer(ecfogdrecord.ECFrefOGDrecordPlayer, DataRow):
    """Display an ECF player record.

    Note that this is the subset of fields copied from master file.

    """

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {
                "text": "Grading code",
                "anchor": tkinter.CENTER,
            },
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 0, "uniform": "pcode"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Name (OGD)", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "pname"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Clubs", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "pclubs"},
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link ECF player record from master file to database."""
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
                WIDGET_CONFIGURE: {"anchor": tkinter.W},
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

        Create textitems argument for ECFrefOGDrowPlayer instance.

        textitems arguments is ignored and is present for compatibility.

        """
        return super().grid_row(
            textitems=(
                self.value.ECFOGDcode,
                self.value.ECFOGDname,
                "\t\t".join(self.value.ECFOGDclubs),
            ),
            **kargs
        )
