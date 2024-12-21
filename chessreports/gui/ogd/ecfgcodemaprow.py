# ecfgcodemaprow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets to display player details with Online Grading List data."""
# class names need to be tidied up

import tkinter

from solentware_grid.gui.datarow import (
    DataRow,
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
)

from ...core import resultsrecord
from ...core.ogd import ecfogdrecord
from ...core.ogd import ecfgcodemaprecord


class ECFmapOGDrowPlayer(resultsrecord.ResultsDBrecordPlayer, DataRow):
    """Display a player record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "ECF code", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "pecfcode"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Name", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "pname"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Event details", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "pevent"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "psection"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Association", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 4, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "paff"},
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link player record to database."""
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
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.W},
                GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.W},
                GRID_CONFIGURE: {"column": 4, "sticky": tkinter.EW},
                ROW: 0,
            },
        ]

    def grid_row(self, textitems=(), **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for ECFmapOGDrowPlayer instance.

        textitems arguments is ignored and is present for compatibility.

        """
        mapcode = ecfgcodemaprecord.get_grading_code_for_person(
            self.database,
            resultsrecord.get_person_from_alias(self.database, self),
        )
        if mapcode:
            ogdrec = ecfogdrecord.get_ecf_ogd_player_for_grading_code(
                self.database, mapcode
            )
            if ogdrec is None:
                mapcode = "*"
            elif ogdrec.value.ECFOGDname is None:
                mapcode = "*"
        else:
            mapcode = ""
        return super().grid_row(
            textitems=(
                mapcode,
                self.value.name,
                resultsrecord.get_event_details(
                    self.database, self.value.event
                ),
                resultsrecord.get_section_details(
                    self.database, self.value.section, self.value.pin
                ),
                resultsrecord.get_affiliation_details(
                    self.database, self.value.affiliation
                ),
            ),
            **kargs
        )
