# events_lite.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Event panel class."""

import tkinter.messagebox

from solentware_misc.core.utilities import AppSysPersonName

from chesscalc.legacy.gui import performance, prediction, population

from ...core import (
    constants,
    filespec,
    resultsrecord,
)
from .. import (
    reports,
)
from .. import events_database
from ..taskpanel import TaskPanel


class Events(events_database.Events):
    """The Events panel for a Results database."""

    btn_performance = "events_performance"
    btn_prediction = "events_prediction"
    btn_population = "events_population"

    # pylint W0102 dangerous-default-value.
    # cnf used as tkinter.Frame argument, which defaults to {}.
    def __init__(self, parent=None, cnf={}, **kargs):
        """Extend and define the results database events panel."""
        super().__init__(parent=parent, cnf=cnf, **kargs)

    def on_performance(self, event=None):
        """Calculate player performances in selected events."""
        del event
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            {
                "runmethod": self.get_appsys()
                .get_results_database()
                .do_database_task,
                "starttaskmsg": "Player performances task started",
                "tabtitle": "Performances",
                "runmethodargs": {
                    "taskmethod": self.calculate_player_performances
                },
                "taskbuttons": {
                    TaskPanel.btn_closebackgroundtask: {
                        "text": "Cancel",
                        "tooltip": "Dismiss the Performance task log.",
                        "underline": 0,
                        "switchpanel": True,
                        "command": False,  # use default on_dismiss
                    },
                },
                "starttaskbuttons": (TaskPanel.btn_closebackgroundtask,),
            }
        )

    def on_prediction(self, event=None):
        """Predict performances for selected events over seasons."""
        del event
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            {
                "runmethod": self.get_appsys()
                .get_results_database()
                .do_database_task,
                "starttaskmsg": "Predictions task started",
                "tabtitle": "Predictions",
                "runmethodargs": {
                    "taskmethod": self.calculate_performance_predictions
                },
                "taskbuttons": {
                    TaskPanel.btn_closebackgroundtask: {
                        "text": "Cancel",
                        "tooltip": "Dismiss the Predictions task log.",
                        "underline": 0,
                        "switchpanel": True,
                        "command": False,  # use default on_dismiss
                    },
                },
                "starttaskbuttons": (TaskPanel.btn_closebackgroundtask,),
            }
        )

    def on_population(self, event=None):
        """Calculate populations."""
        del event
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            {
                "runmethod": self.get_appsys()
                .get_results_database()
                .do_database_task,
                "starttaskmsg": "Population map analysis task started",
                "tabtitle": "Populations",
                "runmethodargs": {
                    "taskmethod": self.calculate_population_map_analysis
                },
                "taskbuttons": {
                    TaskPanel.btn_closebackgroundtask: {
                        "text": "Cancel",
                        "tooltip": (
                            "Dismiss the Population map analysis task log."
                        ),
                        "underline": 0,
                        "switchpanel": True,
                        "command": False,  # use default on_dismiss
                    },
                },
                "starttaskbuttons": (TaskPanel.btn_closebackgroundtask,),
            }
        )

    def describe_buttons(self):
        """Define all action buttons that may appear on events page."""
        super().describe_buttons()
        self.define_button(
            self.btn_performance,
            text="Performances",
            tooltip="Calculate player performances in selected events.",
            underline=3,
            switchpanel=True,
            command=self.on_performance,
        )
        self.define_button(
            self.btn_prediction,
            text="Predictions",
            tooltip="Calculate performance predictions in selected events.",
            underline=5,
            switchpanel=True,
            command=self.on_prediction,
        )
        self.define_button(
            self.btn_population,
            text="Population",
            tooltip="Calculate population map analysis in selected events.",
            underline=1,
            switchpanel=True,
            command=self.on_population,
        )

    def show_event_panel_actions_allowed_buttons(self):
        """Specify buttons to show on events panel."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_dropevent,
                self.btn_join_event_new_players,
                self.btn_exportevents,
                self.btn_performance,
                self.btn_prediction,
                self.btn_population,
                self.btn_game_summary,
                self.btn_event_summary,
            )
        )

    def calculate_performance_predictions(self, database, logwidget):
        """Display performance predictions for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        calculate_events = []
        for e in ebkm:
            calculate_events.append(e)
        for e in esel:
            if e not in ebkm:
                calculate_events.append(e)

        if len(calculate_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot calculate performance predictions",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot calculate performance predictions",
                        "when no events selected.",
                    )
                ),
                title="Events",
            )
            return

        ro = []
        database.start_read_only_transaction()
        try:
            for e in calculate_events:
                rv = resultsrecord.get_event_from_record_value(
                    database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
                ).value
                er = [rv.name, rv.startdate, rv.enddate, rv.name]
                er.extend(
                    [
                        resultsrecord.get_name_from_record_value(
                            database.get_primary_record(
                                filespec.NAME_FILE_DEF, s
                            )
                        ).value.name
                        for s in rv.sections
                    ]
                )
                ro.append(er)
            event_report = []
            for er in sorted(ro):
                event_report.append("\t".join(er[1:]))
            if logwidget:
                logwidget.append_text(
                    "Finding players and game results for selected events"
                )
                logwidget.append_text_only("")
            gefpc = resultsrecord.get_events_for_performance_prediction(
                database, calculate_events
            )
        finally:
            database.end_read_only_transaction()
        if gefpc is None:
            message = " ".join(
                (
                    "Cannot resolve all player identities.  This may be",
                    "because one or more players in the selected events",
                    "have not been merged on the New Players tab.",
                )
            )
            if logwidget:
                logwidget.append_text(message)
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=message,
                title="Events",
            )
            return
        names = gefpc[-1]
        for k in names.keys():
            aspn = AppSysPersonName(names[k])
            names[k] = (aspn.name, names[k])
        if logwidget:
            logwidget.append_text(
                "Calculating performances and season comparisions."
            )
            logwidget.append_text_only("")
        prediction.Prediction(
            self,
            "Calculate  Distributions",
            "\n".join(event_report),
            *gefpc,
            show_report=_PredictionReport
        )
        if logwidget:
            logwidget.append_text("Calculations completed.")
            logwidget.append_text_only("")
        return

    def calculate_player_performances(self, database, logwidget):
        """Display player performances for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        calculate_events = []
        for e in ebkm:
            calculate_events.append(e)
        for e in esel:
            if e not in ebkm:
                calculate_events.append(e)

        if len(calculate_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot calculate player performances",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot calculate player performances",
                        "when no events selected.",
                    )
                ),
                title="Events",
            )
            return

        event_report = []
        database.start_read_only_transaction()
        try:
            for e in calculate_events:
                rv = resultsrecord.get_event_from_record_value(
                    database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
                ).value
                er = [rv.startdate, rv.enddate, rv.name]
                er.extend(
                    [
                        resultsrecord.get_name_from_record_value(
                            database.get_primary_record(
                                filespec.NAME_FILE_DEF, s
                            )
                        ).value.name
                        for s in rv.sections
                    ]
                )
                event_report.append("\t".join(er))
            if logwidget:
                logwidget.append_text(
                    "Finding players and game results for selected events"
                )
                logwidget.append_text_only("")
            gefpc = resultsrecord.get_events_for_performance_calculation(
                database, calculate_events
            )
        finally:
            database.end_read_only_transaction()
        if gefpc is None:
            message = " ".join(
                (
                    "Cannot resolve all player identities.  This may be",
                    "because one or more players in the selected events",
                    "have not been merged on the New Players tab.",
                )
            )
            if logwidget:
                logwidget.append_text_only("")
                logwidget.append_text(message)
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=message,
                title="Events",
            )
            return
        if logwidget:
            logwidget.append_text("Calculating player performances.")
            logwidget.append_text_only("")
        names = gefpc[-1]
        for k in names.keys():
            aspn = AppSysPersonName(names[k])
            names[k] = (aspn.name, names[k])
        performance.Performance(
            self,
            "Calculate Player Performances",
            "\n".join(event_report),
            *gefpc,
            show_report=_PerformanceReport
        )
        if logwidget:
            logwidget.append_text("Calculations completed.")
            logwidget.append_text_only("")
        return

    def calculate_population_map_analysis(self, database, logwidget):
        """Display population map analysis for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        calculate_events = []
        for e in ebkm:
            calculate_events.append(e)
        for e in esel:
            if e not in ebkm:
                calculate_events.append(e)

        if len(calculate_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot calculate population map analysis",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot calculate population map analysis",
                        "when no events selected.",
                    )
                ),
                title="Events",
            )
            return

        ro = []
        database.start_read_only_transaction()
        try:
            for e in calculate_events:
                rv = resultsrecord.get_event_from_record_value(
                    database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
                ).value
                er = [rv.name, rv.startdate, rv.enddate, rv.name]
                er.extend(
                    [
                        resultsrecord.get_name_from_record_value(
                            database.get_primary_record(
                                filespec.NAME_FILE_DEF, s
                            )
                        ).value.name
                        for s in rv.sections
                    ]
                )
                ro.append(er)
            event_report = []
            for er in sorted(ro):
                event_report.append("\t".join(er[1:]))
            if logwidget:
                logwidget.append_text(
                    "Finding players and game results for selected events"
                )
                logwidget.append_text_only("")
            gefpc = resultsrecord.get_events_for_performance_calculation(
                database, calculate_events
            )
        finally:
            database.end_read_only_transaction()
        if gefpc is None:
            message = " ".join(
                (
                    "Cannot resolve all player identities.  This may",
                    "be because one or more players in the selected",
                    "events have not been merged on the New Players",
                    "tab.",
                )
            )
            if logwidget:
                logwidget.append_text(message)
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=message,
                title="Events",
            )
            return
        names = gefpc[-1]
        for k in names.keys():
            aspn = AppSysPersonName(names[k])
            names[k] = (aspn.name, names[k])
        if logwidget:
            logwidget.append_text(
                "Calculating population map analysis and details."
            )
            logwidget.append_text_only("")
        population.Population(
            self,
            "Calculate Population Map Analysis",
            "\n".join(event_report),
            *gefpc,
            show_report=_PopulationReport
        )
        if logwidget:
            logwidget.append_text("Calculations completed.")
            logwidget.append_text_only("")
        return


class _PerformanceReport(reports.ChessResultsReport):
    """Provide initialdir argument for the Save dialogue."""

    configuration_item = constants.RECENT_PERFORMANCES


class _PredictionReport(reports.ChessResultsReport):
    """Provide initialdir argument for the Save dialogue."""

    configuration_item = constants.RECENT_PREDICTIONS


class _PopulationReport(reports.ChessResultsReport):
    """Provide initialdir argument for the Save dialogue."""

    configuration_item = constants.RECENT_POPULATION
