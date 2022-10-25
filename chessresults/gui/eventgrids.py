# eventgrids.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database datagrid classes for events.
"""

import tkinter

from solentware_grid.datagrid import DataGridReadOnly
from solentware_grid.core.dataclient import DataSource

from solentware_bind.gui import gridbindings

from .resultsrow import ResultsDBrowEvent
from ..core import filespec


class EventBaseGrid(gridbindings.GridBindings, DataGridReadOnly):

    """Base class for grid widgets used on event page."""

    def __init__(self, **kwargs):
        """Extend and bind grid navigation within page commands to events"""
        super().__init__(**kwargs)
        self.bindings()

    def show_popup_menu_no_row(self, event=None):
        """Override superclass to do nothing"""
        # Added when DataGridBase changed to assume a popup menu is available
        # when right-click done on empty part of data drid frame.  The popup is
        # used to show all navigation available from grid: but this is not done
        # in results, at least yet, so avoid the temporary loss of focus to an
        # empty popup menu.


class EventGrid(EventBaseGrid):

    """Grid for events recorded."""

    def __init__(self, **kwargs):
        """Extend and note sibling grids."""
        super().__init__(**kwargs)
        self.make_header(ResultsDBrowEvent.header_specification)
        ds = DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.EVENT_FILE_DEF,
            filespec.EVENTNAME_FIELD_DEF,
            ResultsDBrowEvent,
        )
        self.set_data_source(ds)
        self.appsyspanel.get_appsys().get_data_register().register_in(
            self, self.on_data_change
        )
