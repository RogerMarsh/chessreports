# ecfeventcopy.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Panel for copying event details from one event to another."""

import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel

from . import ecfeventgrids


class ECFEventCopy(panel.PanelGridSelector):
    """The Copy Event Detail panel for a Results database."""

    btn_ecfeventcopy = "ecfeventcopy_copy"
    btn_ecfeventback = "ecfeventcopy_back"

    # pylint W0102 dangerous-default-value.
    # cnf used as tkinter.Frame argument, which defaults to {}.
    def __init__(self, parent=None, cnf={}, **kargs):
        """Extend and define the results database ECF events panel."""
        self.eventgrid = None
        super().__init__(parent=parent, cnf=cnf, **kargs)
        self.show_panel_buttons(
            (
                self.btn_ecfeventcopy,
                self.btn_ecfeventback,
            )
        )
        self.create_buttons()
        # pylint W0632 unbalanced-tuple-unpacking.
        # self.make_grids returns a list with same length as argument.
        (self.eventgrid,) = self.make_grids(
            (
                {
                    "grid": ecfeventgrids.ECFEventGrid,
                    "gridfocuskey": "<KeyPress-F7>",
                },
            )
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """

    def describe_buttons(self):
        """Define all action buttons that may appear on ECF events page."""
        super().describe_buttons()
        self.define_button(
            self.btn_ecfeventcopy,
            text="Copy to Event Detail",
            tooltip="Copy data to, and return to, edit Event Details.",
            switchpanel=True,
            underline=0,
            command=self.on_copy_to_ecf_event_detail,
        )
        self.define_button(
            self.btn_ecfeventback,
            text="Back to Event Detail",
            tooltip="Return to edit Event Details without copying data.",
            switchpanel=True,
            underline=0,
            command=self.on_back_to_ecf_event_detail,
        )

    def is_event_selected(self):
        """Return True if events selected.  Otherwise False."""
        if len(self.eventgrid.selection) == 0:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No event selected for amendment of detail",
                title="ECF Events",
            )
            return False
        return True

    def on_copy_to_ecf_event_detail(self, event=None):
        """Do processing for buttons with command set to on_ecf_event_detail.

        Abandon processing if no record selected.

        """
        del event
        if not self.is_event_selected():
            return "break"
        app = self.get_appsys()
        if app.get_tab_data(app.tab_ecfeventdetail).copy_event_detail(
            self.eventgrid.selection
        ):
            return None
        tkinter.messagebox.showinfo(
            parent=self.get_widget(),
            message="No ECF event details found to copy",
            title="ECF Events",
        )
        return "break"

    def on_back_to_ecf_event_detail(self, event=None):
        """Do processing for buttons with command set to on_ecf_event_detail.

        Abandon processing if no record selected.

        """
        del event
