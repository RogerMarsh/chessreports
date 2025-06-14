# leagues_database.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Leagues frame class."""

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os

# __import__ is still used in places, a legacy of pre-3.1 origin of module.
import importlib

from solentware_base import modulequery

from chessvalidate.gui import leagues_validate

from ..core.takeonseason import TakeonSeason
from . import sourceedit
from . import takeonedit
from . import control_database
from . import events_database
from . import newplayers_database
from . import players
from . import importevents
from . import taskpanel
from . import joineventplayers
from ..core.filespec import FileSpec
from .. import APPLICATION_DATABASE_MODULE, ERROR_LOG
from .. import KNOWN_NAME_DATASOURCE_MODULE
from ..core import configuration
from ..core import constants


# Convert module constants _ResultsDB and others to class attribute
# names because the default class-attribute-naming-style is 'any'.
class _Import:
    """Names of classes imported by import_module from alternative modules.

    For runtime "from <db|dpt>reports import ResultsDatabase" and similar.
    """

    ResultsDatabase = "ResultsDatabase"
    DataSourceSet = "DataSourceSet"
    KnownNamesDS = "KnownNamesDS"


class Leagues(leagues_validate.Leagues):
    """The Results frame for a Results database."""

    _menu_opentakeondata = "leagues_database_menu_opentakeondata"

    _tab_control = "leagues_database_tab_control"
    _tab_events = "leagues_database_tab_events"
    _tab_players = "leagues_database_tab_players"
    _tab_newplayers = "leagues_database_tab_newplayers"
    _tab_takeonedit = "leagues_database_tab_takeonedit"
    _tab_importevents = "leagues_database_tab_importevents"
    _tab_reportevent = "leagues_database_tab_reportevent"
    _tab_joineventplayers = "leagues_database_joineventplayers"

    _state_dbopen = "leagues_database_state_dbopen"
    _state_dataopen_dbopen = "leagues_database_state_dataopen_dbopen"
    _state_takeonopen = "leagues_database_state_takeonopen"
    _state_takeonopen_dbopen = "leagues_database_state_takeonopen_dbopen"
    _state_dbopen_import_events = "leagues_database_state_dbopen_import_events"
    _state_dbopen_report_event = "leagues_database_state_dbopen_report_event"
    _state_joineventplayers = "leagues_database_state_joineventplayers"

    show_master_list_grading_codes = False
    show_grading_list_grading_codes = False

    def __init__(self, master=None, cnf=None, **kargs):
        """Extend and define the results database results frame."""
        super().__init__(master=master, cnf=cnf, **kargs)
        self.database = None
        self.database_folder = None
        self._database_modulename = None
        self._knownnamesdatasource_module = None
        self._knownnames_class = None
        self._database_class = None
        self._database_enginename = None

    def define_menus(self):
        """Override.  Define the application menus."""
        menu1 = tkinter.Menu(self.menubar, tearoff=False)
        menu1.add_command(
            label="Open",
            underline=0,
            command=self.try_command(self.database_open, menu1),
        )
        menu1.add_command(
            label="New",
            underline=0,
            command=self.try_command(self.database_new, menu1),
        )
        menu1.add_command(
            label="Close",
            underline=0,
            command=self.try_command(self.database_close, menu1),
        )
        menu1.add_separator()
        menu1.add_command(
            label="Delete",
            underline=0,
            command=self.try_command(self.database_delete, menu1),
        )
        menu2 = tkinter.Menu(self.menubar, tearoff=False)
        menu2.add_command(
            label="Open",
            underline=0,
            command=self.try_command(self.results_open, menu2),
        )
        menu2.add_command(
            label="Take On",
            underline=0,
            command=self.try_command(self.takeon_open, menu2),
        )
        menu2.add_command(
            label="Close",
            underline=0,
            command=self.try_command(self.results_close, menu2),
        )

        # subclasses may want to add commands to menu2
        self.menu_results = menu2

        self.menubar.add_cascade(label="Documents", menu=menu2, underline=0)
        self.menubar.add_cascade(label="Results", menu=menu1, underline=0)

    def define_tabs(self):
        """Define the application tabs."""
        super().define_tabs()
        self.define_tab(
            self._tab_control,
            text="Administration",
            tooltip="Open and close databases and import data.",
            underline=0,
            tabclass=lambda **k: self.results_control(**k),
            create_actions=(control_database.Control.btn_opendatabase,),
            destroy_actions=(control_database.Control.btn_closedatabase,),
        )
        self.define_tab(
            self._tab_events,
            text="Events",
            tooltip="Export event data",
            underline=0,
            tabclass=lambda **k: self.results_events(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control_database.Control.btn_closedatabase,),
        )
        self.define_tab(
            self._tab_takeonedit,
            text="Edit",
            tooltip=(
                " ".join(
                    (
                        "Edit data take-on source files and generate",
                        "Results database input.",
                    )
                )
            ),
            underline=-1,
            tabclass=lambda **k: takeonedit.TakeonEdit(**k),
            destroy_actions=(takeonedit.TakeonEdit.btn_closedata,),
        )
        self.define_tab(
            self._tab_newplayers,
            text="NewPlayers",
            tooltip="Identify new players and merge with existing players.",
            underline=0,
            tabclass=lambda **k: self.results_newplayers(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control_database.Control.btn_closedatabase,),
        )
        self.define_tab(
            self._tab_players,
            text="Players",
            tooltip="Merge or separate existing players.",
            underline=0,
            tabclass=lambda **k: players.Players(gridhorizontal=False, **k),
            destroy_actions=(control_database.Control.btn_closedatabase,),
        )
        self.define_tab(
            self._tab_joineventplayers,
            text="Join Event Players",
            tooltip="Join an event's players with same-named players.",
            underline=-1,
            tabclass=lambda **k: joineventplayers.JoinEventPlayers(**k),
            destroy_actions=(
                joineventplayers.JoinEventPlayers.btn_cancel,
                control_database.Control.btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_importevents,
            text="Import Events",
            tooltip="Import event data",
            underline=-1,
            tabclass=lambda **k: importevents.ImportEvents(**k),
            destroy_actions=(
                importevents.ImportEvents.btn_closeimport,
                control_database.Control.btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_reportevent,
            text="Background Task",
            tooltip="Default background task log",
            underline=-1,
            tabclass=lambda **k: taskpanel.TaskPanel(**k),
            destroy_actions=(
                taskpanel.TaskPanel.btn_closebackgroundtask,
                control_database.Control.btn_closedatabase,
            ),
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
                ),
                self._state_dataopen_dbopen: (self._tab_sourceedit,),
                self._state_takeonopen: (self._tab_takeonedit,),
                self._state_takeonopen_dbopen: (self._tab_takeonedit,),
                self._state_dbopen_import_events: (self._tab_importevents,),
                self._state_dbopen_report_event: (self._tab_reportevent,),
                self._state_joineventplayers: (self._tab_joineventplayers,),
            }
        )
        return tab_states

    def define_state_switch_table(self):
        """Return dict of tuple(<state>, <action>):list(<state>, <tab>)."""
        switch_table = super().define_state_switch_table()
        switch_table.update(
            {
                (self._state_dbopen, self._menu_opendata): [
                    self._state_dataopen_dbopen,
                    self._tab_sourceedit,
                ],
                (self._state_dbclosed, self._menu_opentakeondata): [
                    self._state_takeonopen,
                    self._tab_takeonedit,
                ],
                (self._state_dbopen, self._menu_opentakeondata): [
                    self._state_takeonopen_dbopen,
                    self._tab_takeonedit,
                ],
                (
                    self._state_dbclosed,
                    control_database.Control.btn_opendatabase,
                ): [self._state_dbopen, self._tab_events],
                (
                    self._state_dataopen,
                    control_database.Control.btn_opendatabase,
                ): [self._state_dataopen_dbopen, self._tab_sourceedit],
                (
                    self._state_takeonopen,
                    control_database.Control.btn_opendatabase,
                ): [self._state_takeonopen_dbopen, self._tab_takeonedit],
                (
                    self._state_dataopen_dbopen,
                    sourceedit.SourceEdit.btn_closedata,
                ): [self._state_dbopen, self._tab_events],
                (
                    self._state_takeonopen,
                    takeonedit.TakeonEdit.btn_closedata,
                ): [self._state_dbclosed, None],
                (
                    self._state_takeonopen_dbopen,
                    takeonedit.TakeonEdit.btn_closedata,
                ): [self._state_dbopen, self._tab_events],
                (
                    self._state_dbopen,
                    control_database.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_dataopen_dbopen,
                    control_database.Control.btn_closedatabase,
                ): [self._state_dataopen, self._tab_sourceedit],
                (
                    self._state_takeonopen_dbopen,
                    control_database.Control.btn_closedatabase,
                ): [self._state_takeonopen, self._tab_takeonedit],
                (
                    self._state_dbopen,
                    control_database.Control.btn_importevents,
                ): [
                    self._state_dbopen_import_events,
                    self._tab_importevents,
                ],
                (
                    self._state_dbopen,
                    events_database.Events.btn_join_event_new_players,
                ): [self._state_joineventplayers, self._tab_joineventplayers],
                (
                    self._state_joineventplayers,
                    joineventplayers.JoinEventPlayers.btn_cancel,
                ): [self._state_dbopen, self._tab_events],
                (
                    self._state_dbopen_import_events,
                    importevents.ImportEvents.btn_closeimport,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_dbopen,
                    events_database.Events.btn_exportevents,
                ): [
                    self._state_dbopen_report_event,
                    self._tab_reportevent,
                ],
                (
                    self._state_dbopen,
                    events_database.Events.btn_event_summary,
                ): [
                    self._state_dbopen_report_event,
                    self._tab_reportevent,
                ],
                (
                    self._state_dbopen,
                    events_database.Events.btn_game_summary,
                ): [
                    self._state_dbopen_report_event,
                    self._tab_reportevent,
                ],
                (
                    self._state_dbopen_report_event,
                    taskpanel.TaskPanel.btn_closebackgroundtask,
                ): [self._state_dbopen, self._tab_events],
                (
                    self._state_dbopen_report_event,
                    control_database.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_dbopen_import_events,
                    control_database.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_joineventplayers,
                    control_database.Control.btn_closedatabase,
                ): [self._state_dbclosed, None],
            }
        )
        return switch_table

    def add_ecf_url_item(self, menu):
        """Override in subclasses if edit ECF URL defaults needed."""

    def database_close(self):
        """Close results database."""
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Close",
                message="No results database open",
            )
        elif self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Close",
                message="Database interface not defined",
            )
        else:
            dlg = tkinter.messagebox.askquestion(
                parent=self.get_widget(),
                title="Close",
                message="Close results database",
            )
            if dlg == tkinter.messagebox.YES:
                self._database_close()
                self.database = None
                self.switch_context(control_database.Control.btn_closedatabase)
                self.set_error_file_on_close_database()
                # return False to inhibit context switch if invoked from close
                # Database button on tab because no state change is, or can be,
                # defined for that button.  The switch_context call above has
                # done what is needed.
                return False
        return None

    def database_delete(self):
        """Delete results database."""
        if self.database is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Delete",
                message="".join(
                    (
                        "Delete will not delete a database unless it can be ",
                        "opened.\n\nOpen the database and then Delete it.",
                    )
                ),
            )
            return
        dlg = tkinter.messagebox.askquestion(
            parent=self.get_widget(),
            title="Delete",
            message="".join(
                (
                    "Please confirm that the results database in\n\n",
                    self.database.home_directory,
                    "\n\nis to be deleted.",
                )
            ),
        )
        if dlg == tkinter.messagebox.YES:
            # Replicate _database_close replacing close_database() call with
            # delete_database() call.  The close_database() call just before
            # setting database to None is removed.  The 'database is None'
            # test is done at start of this method.
            try:
                self.get_control_context().close_resources()
            except AttributeError:
                if self.get_control_context() is not None:
                    raise
            message = self.database.delete_database()
            if message:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(), title="Delete", message=message
                )

            message = "".join(
                (
                    "The results database in\n\n",
                    self.database.home_directory,
                    "\n\nhas been deleted.",
                )
            )
            self.database = None
            self.switch_context(control_database.Control.btn_closedatabase)
            self.set_error_file_on_close_database()
            tkinter.messagebox.showinfo(
                parent=self.get_widget(), title="Delete", message=message
            )
        else:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Delete",
                message="The results database has not been deleted",
            )

    def database_new(self):
        """Create and open a new results database."""
        if self.database is not None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="A results database is already open",
                title="New",
            )
            return

        conf = configuration.Configuration()
        database_folder = tkinter.filedialog.askdirectory(
            parent=self.get_widget(),
            title="Select folder for new results database",
            initialdir=conf.get_configuration_value(constants.RECENT_DATABASE),
        )
        if not database_folder:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="Create new results database cancelled",
                title="New",
            )
            return

        if os.path.exists(database_folder):
            if modulequery.modules_for_existing_databases(
                database_folder, FileSpec()
            ):
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "A results database already exists in ",
                            os.path.basename(database_folder),
                        )
                    ),
                    title="New",
                )
                return
        else:
            try:
                os.makedirs(database_folder)
            except OSError:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Folder ",
                            os.path.basename(database_folder),
                            " already exists",
                        )
                    ),
                    title="New",
                )
                return
        conf.set_configuration_value(
            constants.RECENT_DATABASE,
            conf.convert_home_directory_to_tilde(database_folder),
        )

        # the default preference order is used rather than ask the user or
        # an order specific to this application.
        idm = modulequery.installed_database_modules()
        if len(idm) == 0:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "No modules able to create database in\n\n",
                        os.path.basename(database_folder),
                        "\n\navailable.",
                    )
                ),
                title="New",
            )
            return
        _modulename = None
        _enginename = None
        for e in modulequery.DATABASE_MODULES_IN_DEFAULT_PREFERENCE_ORDER:
            if e in idm:
                if e in APPLICATION_DATABASE_MODULE:
                    _enginename = e
                    _modulename = APPLICATION_DATABASE_MODULE[e]
                    break
        if _modulename is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "None of the available database engines can be ",
                        "used to create a database.",
                    )
                ),
                title="New",
            )
            return
        self._open_database_with_engine(
            database_folder, _modulename, _enginename, "New", "create"
        )

    def database_open(self):
        """Open results database."""
        if self.database is not None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="A results database is already open",
                title="Open",
            )
            return

        conf = configuration.Configuration()
        if self.database_folder is None:
            initdir = conf.get_configuration_value(constants.RECENT_DATABASE)
        else:
            initdir = self.database_folder
        database_folder = tkinter.filedialog.askdirectory(
            parent=self.get_widget(),
            title="Select folder containing a results database",
            initialdir=initdir,
            mustexist=tkinter.TRUE,
        )
        if not database_folder:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="Open results database cancelled",
                title="Open",
            )
            return
        conf.set_configuration_value(
            constants.RECENT_DATABASE,
            conf.convert_home_directory_to_tilde(database_folder),
        )

        ed = modulequery.modules_for_existing_databases(
            database_folder, FileSpec()
        )
        # A database module is chosen when creating the database
        # so there should be either only one entry in edt or None
        if not ed:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Folder ",
                        os.path.basename(database_folder),
                        " does not contain a results database",
                    )
                ),
                title="Open",
            )
            return
        if len(ed) > 1:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "There is more than one results database in folder",
                        "\n\n",
                        os.path.basename(database_folder),
                        "\n\nMove the databases to separate folders and try ",
                        "again.  (Use the platform tools for moving files to ",
                        "relocate the database files.)",
                    )
                ),
                title="Open",
            )
            return

        idm = modulequery.installed_database_modules()
        _enginename = None
        for k, v in idm.items():
            if v in ed[0]:
                if _enginename:
                    tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "Several modules able to open database in\n\n",
                                os.path.basename(database_folder),
                                "\n\navailable.  Unable to choose.",
                            )
                        ),
                        title="Open",
                    )
                    return
                _enginename = k
        if _enginename is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "No modules able to open database in\n\n",
                        os.path.basename(database_folder),
                        "\n\navailable.",
                    )
                ),
                title="Open",
            )
            return
        _modulename = APPLICATION_DATABASE_MODULE[_enginename]
        self._open_database_with_engine(
            database_folder, _modulename, _enginename, "Open", "open"
        )

    def _open_database_with_engine(
        self, database_folder, _modulename, _enginename, title, action
    ):
        """Open results database with database engine."""
        if self._database_modulename != _modulename:
            if self._database_modulename is not None:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "The database engine needed for this database is ",
                            "not the one already in use.\n\nYou will have to ",
                            "Quit and start the application again to ",
                            action,
                            " this database.",
                        )
                    ),
                    title=title,
                )
                return
            self._database_enginename = _enginename
            self._database_modulename = _modulename

            def import_name(modulename, name):
                try:
                    module = __import__(
                        modulename, globals(), locals(), [name]
                    )
                except ImportError:
                    return None
                return getattr(module, name)

            self._database_class = import_name(
                _modulename, _Import.ResultsDatabase
            )
            self._knownnames_class = import_name(
                # See comments for set_knownnamesdatasource_module() method.
                # The _knownnames_modulename class attributes should be
                # redundant.
                # pylint: disable-next=protected-access
                self._database_class._knownnames_modulename,
                _Import.KnownNamesDS,
            )
            self.set_ecfdataimport_module(_enginename)
            self.set_ecfogddataimport_module(_enginename)
            self.set_knownnamesdatasource_module(_enginename)

        try:
            self._database_open(database_folder)
        except KeyError as exc:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Unable to ",
                        action,
                        " database\n\n",
                        str(database_folder),
                        "\n\nThe reported reason is:\n\n",
                        str(exc),
                    )
                ),
                title=title,
            )
            self._database_close()
            self.database = None

    def _database_open(self, database_folder):
        """Open results database after creating it if necessary."""
        self.database = self._database_class(
            database_folder, **self._resultsdbkargs
        )
        message = self.database.open_database()
        if message:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(), title="Open", message=message
            )
            return
        self.database_folder = database_folder
        self.set_error_file()
        self.set_ecf_url_defaults()
        self.switch_context(control_database.Control.btn_opendatabase)
        self.get_control_context().show_buttons_for_open_database()
        self.get_control_context().create_buttons()

    def database_quit(self):
        """Quit results application."""
        editor = self.get_tab_data(self._tab_sourceedit)
        if not editor:
            editor = self.get_tab_data(self._tab_takeonedit)
        if not editor:
            if not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                message="Do you really want to quit?",
                title="Quit Results",
            ):
                return False
        elif self.results_data:
            if editor.is_report_modified():
                if not tkinter.messagebox.askyesno(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Event data has been modified.\n\n",
                            "Do you want to quit anyway?\n\n",
                            "The save dialogue will be shown before quitting.",
                        )
                    ),
                    title="Quit Results",
                ):
                    return False
                editor.save_data_folder()
            elif not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                message="Do you really want to quit?",
                title="Quit Results",
            ):
                return False
        self._database_quit()
        self.get_widget().winfo_toplevel().destroy()
        return None

    def results_control(self, **kargs):
        """Return control_database.Control class instance."""
        return control_database.Control(**kargs)

    def results_events(self, **kargs):
        """Return events_database.Events class instance."""
        return events_database.Events(**kargs)

    def results_newplayers(self, **kargs):
        """Return newplayers_database.NewPlayers class instance."""
        return newplayers_database.NewPlayers(**kargs)

    def get_control_context(self):
        """Return the database control page."""
        return self.get_tab_data(self._tab_control)

    def get_database_class(self):
        """Return the database interface class."""
        return self._database_class

    def get_knownnamesdatasource_module(self):
        """Return the known names datasource module."""
        return self._knownnamesdatasource_module

    def get_results_database(self):
        """Return the open database."""
        return self.database

    def results_close(self):
        """Close results source document."""
        if self.results_data is None:
            return
        if tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Close\n",
                    self._results_folder,
                    "\nfolder containing results data",
                )
            ),
            title="Close",
        ):
            self.close_event_edition_results()
            if self.get_state() in (
                self._state_takeonopen_dbopen,
                self._state_takeonopen,
            ):
                self.switch_context(takeonedit.TakeonEdit.btn_closedata)
            else:
                self.switch_context(sourceedit.SourceEdit.btn_closedata)
            self.set_error_file_on_close_source()

    def set_takeon_edit_context(self):
        """Display results take on edit page and hide open database if any."""
        self.switch_context(self._menu_opentakeondata)

    def takeon_close(self):
        """Close results data take-on source document."""
        if self.results_data is None:
            return
        if tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Close\n",
                    self._results_folder,
                    "\nfolder containing results data",
                )
            ),
            title="Close",
        ):
            self.close_event_edition_results()
            self.switch_context(sourceedit.SourceEdit.btn_closedata)
            self.set_error_file_on_close_source()

    def takeon_open(self):
        """Open results data take on documents."""
        ro = self._takeon_open(TakeonSeason)
        if ro:
            self.set_error_file()
            self.set_takeon_edit_context()
            return True
        return None

    def _database_close(self):
        """Close results database."""
        if self.database is None:
            return
        try:
            self.get_control_context().close_resources()
        except AttributeError:
            if self.get_control_context() is not None:
                raise
        self.database.close_database()

    def _database_quit(self):
        """Quit Results."""
        if self.database is None:
            return
        self._database_close()
        self.database = None

    @staticmethod
    def document_edit(**kargs):
        """Return sourceedit.SourceEdit class instance."""
        return sourceedit.SourceEdit(**kargs)

    def _takeon_open(self, eventseason, title=" "):
        """Open results data take on source documents."""
        title = "".join(("Open", title, "Documents"))

        if not self.is_state_switch_allowed(self._menu_opentakeondata):
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=(
                    "Cannot open a Data Takeon folder from the current tab"
                ),
                title=title,
            )
            return None

        if self.results_data is not None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Close the source documents in\n",
                        self._results_folder,
                        "\nfirst.",
                    )
                ),
                title=title,
            )
            return None

        if self._results_folder is None:
            initdir = "~"
        else:
            initdir = self._results_folder
        _results_folder = tkinter.filedialog.askdirectory(
            parent=self.get_widget(),
            title=" ".join((title, "folder")),
            initialdir=initdir,
        )
        if _results_folder:
            results_data = eventseason(_results_folder)
            if not os.path.exists(_results_folder):
                if not tkinter.messagebox.askyesno(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            _results_folder,
                            "\ndoes not exist.",
                            "\nConfirm that a folder is to be created ",
                            "containing new empty documents.",
                        )
                    ),
                    title=title,
                ):
                    return None
                try:
                    os.makedirs(_results_folder)
                except OSError:
                    tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message=" ".join(
                            (_results_folder, "\ncould not be created.")
                        ),
                        title=title,
                    )
                    return None
            if results_data.open_documents(self.get_widget()):
                self.results_data = results_data
                self._results_folder = _results_folder
                return True
        return None

    def set_error_file(self):
        """Set the error log for file being opened.

        If a database is open use the database error log, otherwise use the
        error log for the source documents.

        """
        if self.database is None:
            super().set_error_file()
        else:
            Leagues.set_error_file_name(
                os.path.join(self.database_folder, ERROR_LOG)
            )

    def set_error_file_on_close_source(self):
        """Set the error log after source file is closed.

        If a database is open use the database error log, otherwise None.

        """
        if self.database is None:
            super().set_error_file_on_close_source()
        else:
            Leagues.set_error_file_name(
                os.path.join(self.database_folder, ERROR_LOG)
            )

    def set_error_file_on_close_database(self):
        """Set the error log after database is closed.

        If a source document is open use it's error log, otherwise None.

        """
        if self.results_data is None:
            Leagues.set_error_file_name(None)
        else:
            Leagues.set_error_file_name(
                os.path.join(self._results_folder, ERROR_LOG)
            )

    # It is not clear why both this method, and the direct imports to
    # self._knownnames_class in database_new() and database_open(), exist.
    # Also puzzling is that none of this seems to be used.
    # The leagues module did override this method until support for
    # 'Join Event New Players' was moved to the events_lite module, where it
    # probably should have been all along.
    # (However it's presence did expose problems in the conditional imports in
    #  the database_new() and database_open() methods via a typo in the vedis
    #  and unqlite resultsdatabase modules!)
    def set_knownnamesdatasource_module(self, enginename):
        """Import the known names datasource module."""
        self._knownnamesdatasource_module = importlib.import_module(
            KNOWN_NAME_DATASOURCE_MODULE[enginename], "chessreports.gui"
        )

    def get_event_detail_context(self):
        """Return the event page."""
        return self.get_tab_data(self._tab_events)
