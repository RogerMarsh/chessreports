# resultsrow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display details of events and players."""

import tkinter

from solentware_grid.gui.datarow import (
    DataRow,
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
)

from ..core import resultsrecord
from ..core import filespec


class ResultsDBrowEvent(resultsrecord.ResultsDBrecordEvent, DataRow):
    """Display an Event record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Start date", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 0, "uniform": "edate"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "End date", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 0, "uniform": "edate"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Name", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "ename"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Sections", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "esections"},
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link event record without affiliation to database."""
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
                WIDGET_CONFIGURE: {"anchor": tkinter.CENTER},
                GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.W},
                GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
                ROW: 0,
            },
        ]

    def grid_row(self, textitems=(), **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for ResultsDBrowEvent instance.

        textitems arguments is ignored and is present for compatibility.

        """
        st = []
        for s in self.value.sections:
            st.append(
                resultsrecord.get_name_from_record_value(
                    self.database.get_primary_record(filespec.NAME_FILE_DEF, s)
                )
            )

        return super().grid_row(
            textitems=(
                "".join((self.value.startdate, "\t")),
                "".join((self.value.enddate, "\t")),
                self.value.name,
                "\t".join([s.value.name.strip() for s in st]),
            ),
            **kargs
        )


class ResultsDBrowIdentity(resultsrecord.ResultsDBrecordPlayer, DataRow):
    """Display an identified player record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Name", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "iname"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Event details", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "ievent"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "isection"},
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link identified player record to database."""
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

        Create textitems argument for ResultsDBrowIdentity instance.

        textitems arguments is ignored and is present for compatibility.

        """
        return super().grid_row(
            textitems=(
                self.value.name,
                resultsrecord.get_event_details(
                    self.database, self.value.event
                ),
                resultsrecord.get_section_details(
                    self.database, self.value.section, self.value.pin
                ),
            ),
            **kargs
        )


class ResultsDBrowNewPlayer(resultsrecord.ResultsDBrecordPlayer, DataRow):
    """Display a new player record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Name", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npname"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Event details", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npevent"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npsection"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Association", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npaff"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Reported Codes", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 4, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npcodes"},
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link new player record to database."""
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

        Create textitems argument for ResultsDBrowNewPlayer instance.

        textitems arguments is ignored and is present for compatibility.

        """
        if self.value.reported_codes:
            reportedcodes = "   ".join(self.value.reported_codes)
        else:
            reportedcodes = ""
        return super().grid_row(
            textitems=(
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
                reportedcodes,
            ),
            **kargs
        )


class ResultsDBrowAlias(resultsrecord.ResultsDBrecordPlayer, DataRow):
    """Display an alias record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Name", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npname"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Event details", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npevent"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npsection"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Association", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "npaff"},
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link new player record to database."""
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
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.W},
                GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
                ROW: 0,
            },
        ]

    def grid_row(self, textitems=(), **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for ResultsDBrowAlias instance.

        textitems arguments is ignored and is present for compatibility.

        """
        return super().grid_row(
            textitems=(
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


class ResultsDBrowPlayer(resultsrecord.ResultsDBrecordPlayer, DataRow):
    """Display a player record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Name", "anchor": tkinter.CENTER},
            GRID_CONFIGURE: {"column": 0, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "pname"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Event details", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 1, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "pevent"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 2, "sticky": tkinter.EW},
            GRID_COLUMNCONFIGURE: {"weight": 1, "uniform": "psection"},
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: {"text": "Association", "anchor": tkinter.W},
            GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
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
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: {"anchor": tkinter.W},
                GRID_CONFIGURE: {"column": 3, "sticky": tkinter.EW},
                ROW: 0,
            },
        ]

    def grid_row(self, textitems=(), **kargs):
        """Return tuple of instructions to create row.

        Create textitems argument for ResultsDBrowPlayer instance.

        textitems arguments is ignored and is present for compatibility.

        """
        return super().grid_row(
            textitems=(
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
