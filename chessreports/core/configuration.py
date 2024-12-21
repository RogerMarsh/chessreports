# configuration.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""AAccess and update items in a configuration file.

The initial values are taken from file named in self._CONFIGURATION in the
user's home directory if the file exists.

"""
from solentware_misc.core import configuration

import ecfformat.core.constants

import chessvalidate.core.constants

from . import constants


class Configuration(configuration.Configuration):
    """Identify configuration and recent files and delegate to superclass."""

    _CONFIGURATION = ".chessreports.conf"
    _DEFAULT_ITEM_VAULES = (
        (constants.RECENT_DATABASE, "~"),
        (chessvalidate.core.constants.RECENT_EMAIL_SELECTION, "~"),
        (chessvalidate.core.constants.RECENT_EMAIL_EXTRACTION, "~"),
        (chessvalidate.core.constants.RECENT_CSV_DOWNLOAD, "~"),
        (chessvalidate.core.constants.RECENT_DOCUMENT, "~"),
        (constants.RECENT_SUBMISSION, "~"),
        (constants.RECENT_SOURCE_SUBMISSION, "~"),
        (constants.RECENT_FEEDBACK, "~"),
        (constants.RECENT_FEEDBACK_EMAIL, "~"),
        (constants.RECENT_MASTERFILE, "~"),
        (constants.RECENT_IMPORT_EVENTS, "~"),
        (constants.RECENT_EXPORT_EVENTS, "~"),
        (constants.RECENT_PERFORMANCES, "~"),
        (constants.RECENT_PREDICTIONS, "~"),
        (constants.RECENT_POPULATION, "~"),
        (constants.RECENT_GAME_SUMMARY, "~"),
        (constants.RECENT_EVENT_SUMMARY, "~"),
        (constants.RECENT_GRADING_LIST, "~"),
        (constants.RECENT_RATING_LIST, "~"),
        (ecfformat.core.constants.RECENT_RESULTS_FORMAT_FILE, "~"),
        (
            ecfformat.core.constants.SHOW_VALUE_BOUNDARY,
            ecfformat.core.constants.SHOW_VALUE_BOUNDARY_TRUE,
        ),
    )
