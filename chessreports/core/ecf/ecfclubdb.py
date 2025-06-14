# ecfclubdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Classes to open ECF club files and extract records."""

import io
from os.path import split

from solentware_base.core.record import KeydBaseIII, Value, RecorddBaseIII

from ...minorbases.dbaseapi import (
    DBaseapi,
    FIELDS,
    FILE,
    C,
    LENGTH,
    TYPE,
    START,
)

CLUBS = "clubs"

# The RECTYPE values on an ECF club update file and interpretation
ADDCLUB = "A"  # add a new club
UPDATECLUB = "U"  # update details of existing club
DELETECLUB = "D"  # delete a club


class ECFclubsDB(DBaseapi):
    """Access a club master file published by ECF."""

    def __init__(self, DBpath):
        """Define ECF Club File dBaseIII structure."""
        if isinstance(DBpath, io.BytesIO):
            d, f = False, DBpath
        else:
            d, f = split(DBpath)

        dbnames = {
            CLUBS: {
                FILE: f,
                FIELDS: {
                    "CODE": {START: 1, LENGTH: 4, TYPE: C},
                    "CLUB": {LENGTH: 40, TYPE: C},
                    "COUNTY": {START: 45, LENGTH: 4, TYPE: C},
                },
            },
        }

        DBaseapi.__init__(self, dbnames, d)


class ECFclubsUpdateDB(DBaseapi):
    """Access a club update file published by ECF."""

    def __init__(self, DBpath):
        """Define ECF Club File update dBaseIII structure."""
        if isinstance(DBpath, io.BytesIO):
            d, f = False, DBpath
        else:
            d, f = split(DBpath)

        dbnames = {
            CLUBS: {
                FILE: f,
                FIELDS: {
                    "RECTYPE": {START: 1, LENGTH: 1, TYPE: C},
                    "CODE": {START: 2, LENGTH: 4, TYPE: C},
                    "CLUB": {LENGTH: 40, TYPE: C},
                    "COUNTY": {START: 46, LENGTH: 4, TYPE: C},
                },
            },
        }

        DBaseapi.__init__(self, dbnames, d)


class ECFclubsDBkey(KeydBaseIII):
    """Club key."""


class ECFclubsDBvalue(Value):
    """Club data."""

    # def load(self, value):
    #    """Convert bytes values from dbaseIII record to string"""
    #    super().load(value)
    #    for a in self.__dict__:
    #        self.__dict__[a] = self.__dict__[a]


class ECFclubsDBrecord(RecorddBaseIII):
    """Club record."""

    def __init__(self, keyclass=ECFclubsDBkey, valueclass=ECFclubsDBvalue):
        """Customise RecorddBaseIII with ECFclubsDBkey and ECFclubsDBvalue."""
        super().__init__(keyclass, valueclass)
