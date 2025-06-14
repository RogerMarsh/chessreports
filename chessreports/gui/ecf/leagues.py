# leagues.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Leagues frame class."""

import os
import importlib
import tkinter.messagebox

from solentware_misc.gui.configuredialog import ConfigureDialog

from . import control
from . import events
from . import newplayers
from . import ecfgradingcodes
from . import ecfclubcodes
from . import ecfevents
from . import ecfeventcopy
from . import ecfplayers
from . import importecfdata
from . import feedback
from . import feedback_monthly
from . import activeclubs
from . import ratedplayers
from . import newevent
from .. import leagues_database
from .. import configuredialog_hack
from ... import ECF_DATA_IMPORT_MODULE
from ...core import constants
from ...core import configuration


class Leagues(leagues_database.Leagues):
    """The Results frame for a Results database."""

    tab_ecfeventdetail = "leagues_tab_ecfeventdetail"
    _tab_ecfgradingcodes = "leagues_tab_ecfgradingcodes"
    _tab_ecfclubcodes = "leagues_tab_ecfclubcodes"
    _tab_ecfevents = "leagues_tab_ecfevents"
    _tab_ecfeventcopy = "leagues_tab_ecfeventcopy"
    _tab_ecfplayers = "leagues_tab_ecfplayers"
    _tab_importecfdata = "leagues_tab_importecfdata"
    _tab_importfeedback = "leagues_tab_importfeedback"
    _tab_importfeedbackmonthly = "leagues_tab_importfeedback_monthly"
    _tab_clubsdownload = "leagues_tab_clubsdownload"
    _tab_playersdownload = "leagues_tab_playersdownload"

    _state_ecfeventdetail = "leagues_state_ecfeventdetail"
    _state_ecfeventcopy = "leagues_state_ecfeventcopy"
    _state_importecfdata = "leagues_state_importecfdata"
    _state_importfeedback = "leagues_state_importfeedback"
    _state_importfeedbackmonthly = "leagues_state_importfeedback_monthly"
    _state_responsefeedbackmonthly = "leagues_state_responsefeedback_monthly"
    _state_clubsdownload = "leagues_state_clubsdownload"
    _state_playersdownload = "leagues_state_playersdownload"

    show_master_list_grading_codes = True

    def __init__(self, master=None, cnf=None, **kargs):
        """Extend and define the results database results frame."""
        super().__init__(master=master, cnf=cnf, **kargs)
        self.__ecfdataimport_module = None

    def define_tabs(self):
        """Define the application tabs."""
        super().define_tabs()
        self.define_tab(
            self._tab_ecfgradingcodes,
            text="ECF Codes",
            tooltip="Associate player with ECF code.",
            underline=2,
            tabclass=lambda **k: ecfgradingcodes.ECFGradingCodes(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control.btn_closedatabase,),
        )
        self.define_tab(
            self._tab_ecfclubcodes,
            text="Club Codes",
            tooltip="Associate player with ECF club code.",
            underline=0,
            tabclass=lambda **k: ecfclubcodes.ECFClubCodes(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control.btn_closedatabase,),
        )
        self.define_tab(
            self._tab_ecfevents,
            text="ECF Events",
            tooltip="Select an event to submit to ECF.",
            underline=5,
            tabclass=lambda **k: ecfevents.ECFEvents(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control.btn_closedatabase,),
        )
        self.define_tab(
            self.tab_ecfeventdetail,
            text="ECF Event Detail",
            tooltip="Update details of event for submission to ECF.",
            # pylint W0108 unnecessary-lambda.
            # self.define_tab implementation provides **k arguments.
            tabclass=lambda **k: newevent.NewEvent(**k),
            destroy_actions=(
                newevent.NewEvent.btn_cancel,
                control.Control.btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_ecfeventcopy,
            text="Copy ECF Event Detail",
            tooltip="Select event and copy details to ECF Event Detail tab.",
            # pylint W0108 unnecessary-lambda.
            # self.define_tab implementation provides **k arguments.
            tabclass=lambda **k: ecfeventcopy.ECFEventCopy(**k),
            destroy_actions=(
                newevent.NewEvent.btn_cancel,
                control.Control.btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_ecfplayers,
            text="Player ECF Detail",
            tooltip="Grading codes and club codes allocated to players.",
            underline=3,
            tabclass=lambda **k: ecfplayers.ECFPlayers(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control.btn_closedatabase,),
        )
        self.define_tab(
            self._tab_importecfdata,
            text="Import ECF Reference Data",
            tooltip="Import data from ECF Master and Update zipped files.",
            underline=-1,
            # pylint W0108 unnecessary-lambda.
            # self.define_tab implementation provides **k arguments.
            tabclass=lambda **k: importecfdata.ImportECFData(**k),
            destroy_actions=(
                importecfdata.ImportECFData.btn_closeecfimport,
                control.Control.btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_importfeedback,
            text="Feedback",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            # pylint W0108 unnecessary-lambda.
            # self.define_tab implementation provides **k arguments.
            tabclass=lambda **k: feedback.Feedback(**k),
            destroy_actions=(
                feedback.Feedback.btn_closefeedback,
                control.Control.btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_importfeedbackmonthly,
            text="Feedback Monthly",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            # pylint W0108 unnecessary-lambda.
            # self.define_tab implementation provides **k arguments.
            tabclass=lambda **k: feedback_monthly.FeedbackMonthly(**k),
            destroy_actions=(
                feedback_monthly.FeedbackMonthly.btn_closefeedbackmonthly,
                control.Control.btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_clubsdownload,
            text="Active Clubs Download",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            # pylint W0108 unnecessary-lambda.
            # self.define_tab implementation provides **k arguments.
            tabclass=lambda **k: activeclubs.ActiveClubs(**k),
            destroy_actions=(activeclubs.ActiveClubs.btn_closeactiveclubs,),
        )
        self.define_tab(
            self._tab_playersdownload,
            text="Players Download",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            # pylint W0108 unnecessary-lambda.
            # self.define_tab implementation provides **k arguments.
            tabclass=lambda **k: ratedplayers.RatedPlayers(**k),
            destroy_actions=(ratedplayers.RatedPlayers.btn_closeratedplayers,),
        )

    def define_tab_states(self):
        """Return dict of <state>:tuple(<tab>, ...)."""
        tab_states = super().define_tab_states()
        tab_states.update(
            {
                self._state_dbopen: (
                    self._tab_control,
                    self._tab_events,
                    self._tab_newplayers,
                    self._tab_players,
                    self._tab_ecfgradingcodes,
                    self._tab_ecfclubcodes,
                    self._tab_ecfplayers,
                    self._tab_ecfevents,
                ),
                self._state_ecfeventdetail: (self.tab_ecfeventdetail,),
                self._state_ecfeventcopy: (self._tab_ecfeventcopy,),
                self._state_importecfdata: (self._tab_importecfdata,),
                self._state_importfeedback: (self._tab_importfeedback,),
                self._state_importfeedbackmonthly: (
                    self._tab_importfeedbackmonthly,
                ),
                self._state_responsefeedbackmonthly: (
                    self._tab_importfeedbackmonthly,
                ),
                self._state_clubsdownload: (self._tab_clubsdownload,),
                self._state_playersdownload: (self._tab_playersdownload,),
            }
        )
        return tab_states

    def define_state_switch_table(self):
        """Return dict of tuple(<state>, <action>):list(<state>, <tab>)."""
        switch_table = super().define_state_switch_table()
        switch_table.update(
            {
                (
                    self._state_dbopen,
                    ecfevents.ECFEvents.btn_ecfeventdetail,
                ): [self._state_ecfeventdetail, self.tab_ecfeventdetail],
                (self._state_ecfeventdetail, newevent.NewEvent.btn_copy): [
                    self._state_ecfeventcopy,
                    self._tab_ecfeventcopy,
                ],
                (self._state_ecfeventdetail, newevent.NewEvent.btn_cancel): [
                    self._state_dbopen,
                    self._tab_ecfevents,
                ],
                (
                    self._state_dbopen,
                    control.Control.btn_copyecfmasterplayer,
                ): [self._state_importecfdata, self._tab_importecfdata],
                (self._state_dbopen, control.Control.btn_copyecfmasterclub): [
                    self._state_importecfdata,
                    self._tab_importecfdata,
                ],
                (
                    self._state_importecfdata,
                    importecfdata.ImportECFData.btn_closeecfimport,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_dbopen,
                    control.Control.btn_ecfresultsfeedback,
                ): [self._state_importfeedback, self._tab_importfeedback],
                (
                    self._state_importfeedback,
                    feedback.Feedback.btn_closefeedback,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_dbopen,
                    control.Control.btn_ecfresultsfeedbackmonthly,
                ): [
                    self._state_importfeedbackmonthly,
                    self._tab_importfeedbackmonthly,
                ],
                (
                    self._state_dbopen,
                    ecfevents.ECFEvents.btn_ecf_feedback_monthly,
                ): [
                    self._state_responsefeedbackmonthly,
                    self._tab_importfeedbackmonthly,
                ],
                (
                    self._state_importfeedbackmonthly,
                    feedback_monthly.FeedbackMonthly.btn_closefeedbackmonthly,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_responsefeedbackmonthly,
                    feedback_monthly.FeedbackMonthly.btn_closefeedbackmonthly,
                ): [self._state_dbopen, self._tab_ecfevents],
                (self._state_dbopen, control.Control.btn_clubsdownload): [
                    self._state_clubsdownload,
                    self._tab_clubsdownload,
                ],
                (
                    self._state_clubsdownload,
                    activeclubs.ActiveClubs.btn_closeactiveclubs,
                ): [self._state_dbopen, self._tab_control],
                (self._state_dbopen, control.Control.btn_playersdownload): [
                    self._state_playersdownload,
                    self._tab_playersdownload,
                ],
                (
                    self._state_playersdownload,
                    ratedplayers.RatedPlayers.btn_closeratedplayers,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_ecfeventdetail,
                    control.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_importecfdata,
                    control.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_importfeedback,
                    control.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_importfeedbackmonthly,
                    control.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_responsefeedbackmonthly,
                    control.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_ecfeventcopy,
                    ecfeventcopy.ECFEventCopy.btn_ecfeventcopy,
                ): [
                    self._state_ecfeventdetail,
                    self.tab_ecfeventdetail,
                ],
                (
                    self._state_ecfeventcopy,
                    ecfeventcopy.ECFEventCopy.btn_ecfeventback,
                ): [
                    self._state_ecfeventdetail,
                    self.tab_ecfeventdetail,
                ],
            }
        )
        return switch_table

    def get_ecf_event_detail_context(self):
        """Return the ECF event page."""
        return self.get_tab_data(self._tab_ecfevents)

    def set_ecfdataimport_module(self, enginename):
        """Import the ECF reference data import module."""
        self.__ecfdataimport_module = importlib.import_module(
            ECF_DATA_IMPORT_MODULE[enginename], "chessreports.gui"
        )

    def get_ecfdataimport_module(self):
        """Return the ECF reference data import module."""
        return self.__ecfdataimport_module

    def results_control(self, **kargs):
        """Return control.Control class instance."""
        return control.Control(**kargs)

    def results_events(self, **kargs):
        """Return events.Events class instance."""
        return events.Events(**kargs)

    def results_newplayers(self, **kargs):
        """Return newplayers.NewPlayers class instance."""
        return newplayers.NewPlayers(**kargs)

    def set_ecf_url_defaults(self):
        """Set URL defaults for ECF website.

        Create a file, if it does not exist, with URL defaults in user's
        home directory.

        """
        default = configuration.Configuration().get_configuration_file_name()

        if not os.path.exists(default):
            urls = "\n".join([" ".join(u) for u in constants.DEFAULT_URLS])
            with open(default, "w", encoding="utf8") as outf:
                try:
                    outf.write(urls)
                    outf.write("\n")
                except Exception as exc:
                    tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "Unable to write URL defaults to ",
                                default,
                                "\n\nReported error is ",
                                str(exc),
                            )
                        ),
                        title="Open Database",
                    )
                    return

    def add_ecf_url_item(self, menu):
        """Override to provide edit ECF URL defaults."""
        menu.insert_separator(tkinter.END)
        menu.insert_command(
            tkinter.END,
            label="ECF URLs",
            underline=4,
            command=self.try_command(self.edit_ecf_url_defaults, menu),
        )
        menu.insert_separator(tkinter.END)

    def edit_ecf_url_defaults(self):
        """Edit URL defaults for ECF website if the defaults file exists."""
        url_items = {
            default[0]: default[1] for default in constants.DEFAULT_URLS
        }
        conf = configuration.Configuration()
        conf.get_configuration_text_and_values_for_items_from_file(url_items)
        config_text = []
        for k, v in sorted(url_items.items()):
            config_text.append(
                " ".join((k, conf.get_configuration_value(k, v)))
            )
        config_text = "\n".join(config_text)

        # An unresolved bug is worked around by this 'try ... except' block.
        # The initial exception can be exposed by uncommenting the 'else'
        # block at start of 'except' block.
        # I have no idea what is going on so cannot fix problem.
        try:
            edited_text = ConfigureDialog(
                master=self.get_widget(),
                configuration=config_text,
                dialog_title="Edit ECF URL Defaults",
            ).config_text
        except KeyError as exc:
            if str(exc) != "'#!menu'":
                raise
            # else:
            #    raise
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "The sufficient and necessary actions to reach ",
                        "this point are:\n\n",
                        "Close a database\n",
                        "Use the 'Tools | ECF URLs' menu option.\n\n",
                        "The cause is probably an unresolved bug.\n\n",
                        "The best action now is close and restart the ",
                        "ChessReports application; but there may be ",
                        "nothing wrong with dismissing this message, ",
                        "manually destroying the bare widget, and editing ",
                        "the ECF URLs in the widget that appears.",
                    )
                ),
                title="Edit ECF URL Defaults",
            )
            edited_text = configuredialog_hack.ConfigureDialogHack(
                self.get_widget(),
                configuration=config_text,
                dialog_title="Edit ECF URL Defaults",
            ).config_text

        if edited_text is None:
            return
        conf.set_configuration_values_from_text(
            edited_text, config_items=url_items
        )
