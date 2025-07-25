# selectemail.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Email selection filter User Interface for Results application."""

from chessvalidate.gui import selectemail

from ..core import configuration


class SelectEmail(selectemail.SelectEmail):
    """Add store configuration file to select.Select for opening files."""

    # Some file_new() methods have 'recent=<something>' argument.
    # pylint: disable-next=arguments-differ
    def file_new(self, conf=None):
        """Set configuration then delegate."""
        if conf is None:
            conf = configuration
        super().file_new(conf=conf)

    # Some file_open() methods have 'recent=<something>' argument.
    # pylint: disable-next=arguments-differ
    def file_open(self, conf=None):
        """Set configuration then delegate."""
        if conf is None:
            conf = configuration
        super().file_open(conf=conf)
