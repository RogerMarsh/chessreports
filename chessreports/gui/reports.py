# reports.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Customise solentware_misc.gui.reports AppSysReport class."""

import tkinter.filedialog
import os

from solentware_misc.gui.reports import AppSysReport

from ..core import (
    configuration,
)


# The need for this class demonstrates the show_report() method in
# solentware_misc.gui.reports is useless.
class ChessResultsReport(AppSysReport):
    """Provide initialdir argument for the Save dialogue.

    Subclasses must define a suitable attribute named configuration_item.

    AppSysReport provides the other instance attributes.

    """

    def on_save(self, event=None):
        """Override to support initialdir argument."""
        conf = configuration.Configuration()
        # Attribute is defined as a class attribute in a superclass.
        # pylint: disable-next=no-member
        configuration_item = self.configuration_item
        filepath = tkinter.filedialog.asksaveasfilename(
            parent=self._toplevel,
            title=self._save_title,
            initialdir=conf.get_configuration_value(configuration_item),
            defaultextension=".txt",
        )
        if not filepath:
            return
        conf.set_configuration_value(
            configuration_item,
            conf.convert_home_directory_to_tilde(os.path.dirname(filepath)),
        )
        with open(filepath, mode="wb") as outfile:
            outfile.write(
                self.textreport.get("1.0", tkinter.END).encode("utf8")
            )
