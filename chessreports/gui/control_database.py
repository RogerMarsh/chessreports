# control_database.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Control panel class.

Open and close databases and import and export data functions are available
on this panel.

"""

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os
import bz2

from solentware_misc.gui import panel

from ..core import filespec
from ..core import configuration
from ..core import constants


class Control(panel.PlainPanel):
    """The Control panel for a Results database."""

    btn_opendatabase = "control_lite_open_database"  # menu button only
    btn_closedatabase = "control_lite_close_database"
    btn_importevents = "control_lite_import_events"

    # pylint W0102 dangerous-default-value.
    # cnf used as tkinter.Frame argument, which defaults to {}.
    def __init__(self, parent=None, cnf={}, **kargs):
        """Extend and define the results database control panel."""
        super().__init__(parent=parent, cnf=cnf, **kargs)

        self.datafile = None
        self.datagrid = None

        self.show_buttons_for_closed_database()
        self.create_buttons()

        self.datafilepath = tkinter.Label(master=self.get_widget(), text="")
        self.datafilepath.pack(side=tkinter.TOP, fill=tkinter.X)

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        self.close_resources()

        # try: ... except: ... for application destroyed after Close then Quit.
        # Switch to ChessReports-4.0 introduced raising exception.
        try:
            self.datafilepath.destroy()
        except tkinter.TclError:
            pass

    def close_display_data_for_import(self):
        """Destroy the page displaying data for import."""
        self.datagrid.frame.destroy()
        self.datagrid = None

    def close_import_file(self, inputtype):
        """Close the open file containing data for import."""
        pn = self.datafilepath.cget("text").split()
        pn[0] = os.path.split(pn[0])[-1]
        if tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message=" ".join(
                ("Close", " ".join(pn), "containing", inputtype, "data")
            ),
            title="Close",
        ):
            self.close_resources()
            return True
        return None

    def close_import_file_prompt(self, displaytype):
        """Prompt to close the open file."""
        if self.datafile is not None:
            pn = self.datafilepath.cget("text").split()
            pn[0] = os.path.split(pn[0])[-1]
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(("Close", " ".join(pn), "first")),
                title=displaytype,
            )
            return True
        return None

    def close_resources(self):
        """Close the resources opened from this tab while database open."""
        self.close_update_resources()
        if self.datafile is not None:
            self.datafile.close_context()
            self.datafile = None
            self.datafilepath.configure(text="")
        if self.datagrid is not None:
            self.close_display_data_for_import()

    def close_update_resources(self):
        """Close any open files containing master data from ECF."""

    def describe_buttons(self):
        """Define all action buttons that may appear on Control page."""
        super().describe_buttons()
        self.define_button(
            self.btn_closedatabase,
            text="Shut Database",
            tooltip="Close the open database.",
            underline=9,
            switchpanel=True,
            command=self.on_close_database,
        )
        self.define_button(
            self.btn_importevents,
            text="Import Events",
            tooltip="Import event data exported by Export Events.",
            underline=0,
            switchpanel=True,
            command=self.on_import_events,
        )

    def on_close_database(self, event=None):
        """Do close database actions."""
        del event
        if not self.get_appsys().database_close():
            self.inhibit_context_switch(self.btn_closedatabase)

    def on_import_events(self, event=None):
        """Do import events actions."""
        del event
        conf = configuration.Configuration()
        filepath = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title="Open Event file",
            defaultextension=".bz2",
            filetypes=(("bz2 compressed", "*.bz2"),),
            initialdir=conf.get_configuration_value(
                constants.RECENT_IMPORT_EVENTS
            ),
        )
        if not filepath:
            self.inhibit_context_switch(self.btn_importevents)
            return
        conf.set_configuration_value(
            constants.RECENT_IMPORT_EVENTS,
            conf.convert_home_directory_to_tilde(os.path.dirname(filepath)),
        )
        bz2file = bz2.BZ2File(filepath, "rb")
        text = bz2file.read()
        bz2file.close()

        # The copymethod argument is not used because the processing needed
        # is unlikely to change over time.  (Master lists of grading codes have
        # been the same format since 1999, but frequency of publication and
        # volume of data changes have changed the processing appropriate over
        # time.)
        # GAME_FILE_DEF, PLAYER_FILE_DEF, and EVENT_FILE_DEF, were present
        # before ChessReports-4.0 but DPT file opening method allowed for
        # exceptions on Allocate so the incorrect closecontexts argument did
        # not matter.
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            {
                "datafile": (filepath, text),
                "closecontexts": (
                    filespec.GAME_FILE_DEF,
                    filespec.PLAYER_FILE_DEF,
                    filespec.EVENT_FILE_DEF,
                    filespec.NAME_FILE_DEF,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFCLUB_FILE_DEF,
                    filespec.ECFTXN_FILE_DEF,
                    filespec.MAPECFCLUB_FILE_DEF,
                    filespec.MAPECFPLAYER_FILE_DEF,
                    filespec.ECFEVENT_FILE_DEF,
                    filespec.ECFOGDPLAYER_FILE_DEF,
                    filespec.MAPECFOGDPLAYER_FILE_DEF,
                ),
            }
        )

    def show_buttons_for_closed_database(self):
        """Show buttons for actions allowed when database closed."""
        self.hide_panel_buttons()
        self.show_panel_buttons(())

    def show_buttons_for_open_database(self):
        """Show buttons for actions allowed when database is open."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (self.btn_closedatabase, self.btn_importevents)
        )
