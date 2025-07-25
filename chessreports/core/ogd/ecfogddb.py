# ecfogddb.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Classes to open ECF Online Grading Database files and extract records."""

import csv
import io
from os.path import split

from solentware_base.core.record import KeyText, ValueText, RecordText
from solentware_base.core.constants import FILE, FIELDS

from ...minorbases.textapi import (
    Textapi,
    TextapiRoot,
)

PLAYERS = "ogdplayers"


class ECFOGD(Textapi):
    """Access an Online Grading Database file published by ECF."""

    def __init__(self, DBpath):
        """Define filespec for text in DBpath file, and delegate."""
        if isinstance(DBpath, io.BytesIO):
            d, f = False, DBpath
        else:
            d, f = split(DBpath)

        dbnames = {
            PLAYERS: {
                FILE: f,
                FIELDS: {},
            },
        }

        Textapi.__init__(self, dbnames, d)

    def make_root(self, filename):
        """Return ECFOGDRoot instance for filename."""
        return ECFOGDRoot(filename)


class ECFOGDRoot(TextapiRoot):
    """Provide record access to an Online Grading Database file in bsddb style.

    The CSV file containing the online grading database is displayed as a text
    file.  When updating the database it is processed as a CSV file.  This
    class deals with the special status of the first line of text, which
    contains the field names.
    """

    def __init__(self, *args):
        """Define database structure."""
        super().__init__(*args)
        self.headerline = None
        self.fieldnames = None

    def open_root(self):
        """Delegate then note CSV file fieldnames and row count."""
        super().open_root()
        self.headerline = self.textlines.pop(0)
        self.record_count = len(self.textlines)
        if isinstance(self.headerline, bytes):
            try:
                h = self.headerline.decode("utf8")
            except UnicodeDecodeError:
                h = self.headerline.decode("iso-8859-1")
            self.fieldnames = csv.DictReader([h]).fieldnames
        else:
            self.fieldnames = csv.DictReader([self.headerline]).fieldnames


class ECFOGDkey(KeyText):
    """OGD player key."""


class ECFOGDvalue(ValueText):
    """OGD player data."""


class ECFOGDrecord(RecordText):
    """OGD player record."""

    def __init__(self, keyclass=ECFOGDkey, valueclass=ECFOGDvalue):
        """Customise RecordText with ECFOGDkey and ECFOGDvalue."""
        super().__init__(keyclass, valueclass)
