# ecfrecord.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definition classes for data extracted from ECF master files."""

from ast import literal_eval

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record

from . import ecfclubdb
from . import ecfplayerdb
from .. import filespec

_NEW = "New"
_CHANGE = "Change"
_OLD = "Old"
TXN_FEEDBACK = "Feedback"
TXN_NEW = "New"
TXN_UPDATE = "Update"
OBJTYPE_CLUB = "Club"
OBJTYPE_PLAYER = "Player"

_ecfupdateplayertxns = {
    ecfplayerdb.ADDPLAYER: _NEW,
    ecfplayerdb.UPDATEPLAYER: _CHANGE,
    ecfplayerdb.DELETEPLAYER: _OLD,
}
_ecfupdateclubtxns = {
    ecfclubdb.ADDCLUB: _NEW,
    ecfclubdb.UPDATECLUB: _CHANGE,
    ecfclubdb.DELETECLUB: _OLD,
}
_BAD_TXN = "Unknown"

ECFplayerclubsfields = ("CLUB1", "CLUB2", "CLUB3", "CLUB4", "CLUB5", "CLUB6")

_Eventdictkeys = tuple(
    (
        "ECODE",
        "ENAME",
        "EBCF",
        "EDATE",
        "EFINALDATE",
        "ESUBMISSION",
        "ETREASURER",
        "EADDRESS1",
        "EADDRESS2",
        "EADDRESS3",
        "EADDRESS4",
        "EPOSTCODE",
        "EGRADER",
        "EGADDRESS1",
        "EGADDRESS2",
        "EGADDRESS3",
        "EGADDRESS4",
        "EGPOSTCODE",
        "EFIRSTMOVES",
        "EFIRSTMINUTES",
        "ENEXTMOVES",
        "ENEXTMINUTES",
        "ERESTMINUTES",
        "EALLMINUTES",
        "ESECPERMOVE",
        "EADJUDICATED",
        "EGRANDPRIX",
        "EFIDE",
        "ECHESSMOVES",
        "EEAST",
        "EMIDLAND",
        "ENORTH",
        "ESOUTH",
        "EWEST",
        "ECOLOR",
    )
)
_Playerdictkeys = tuple(
    (
        "PCODE",
        "PNAME",
        "PBCF",
        "PDOB",
        "PGENDER",
        "PDIRECT",
        "PTITLE",
        "PFIDE",
        "PLENFORENAME",
        "PLENNICKNAME",
    )
)


class ECFrefDBkeyECFclub(KeyData):
    """Primary key of club from ECF."""


class ECFrefDBvalueECFclub(Value):
    """Club data from ECF."""

    def __init__(self):
        """Extend Value with ECF club data."""
        super().__init__()
        self.ECFcode = None
        self.ECFactive = False
        self.ECFname = None
        self.ECFcountycode = None

    def load(self, value):
        """Override, extract ECF club data from value into attributes."""
        (
            self.ECFcode,
            self.ECFactive,
            self.ECFname,
            self.ECFcountycode,
        ) = literal_eval(value)

    def pack(self):
        """Extend, return ECF club record and index data."""
        v = super().pack()
        index = v[1]
        index[filespec.ECFCLUBCODE_FIELD_DEF] = [self.ECFcode]
        index[filespec.ECFCLUBNAME_FIELD_DEF] = [self.ECFname]
        return v

    def pack_value(self, *a):
        """Override, return tuple of self attributes."""
        del a
        return repr(
            (self.ECFcode, self.ECFactive, self.ECFname, self.ECFcountycode)
        )


class ECFrefDBrecordECFclub(Record):
    """Club record from ECF."""

    def __init__(
        self, keyclass=ECFrefDBkeyECFclub, valueclass=ECFrefDBvalueECFclub
    ):
        """Customise Record with ECFrefDBkeyECFclub, ECFrefDBvalueECFclub."""
        super().__init__(keyclass, valueclass)


class ECFrefDBkeyECFplayer(KeyData):
    """Primary key of player from ECF."""


class ECFrefDBvalueECFplayer(Value):
    """Player data from ECF."""

    def __init__(self):
        """Extend Value with ECF player details."""
        super().__init__()
        self.ECFcode = None
        self.ECFactive = False
        self.ECFname = None
        self.ECFclubcodes = []
        self.ECFmerge = None

    def load(self, value):
        """Override, extract ECF player data from value into attributes."""
        (
            self.ECFcode,
            self.ECFactive,
            self.ECFname,
            self.ECFclubcodes,
            self.ECFmerge,
        ) = literal_eval(value)

    def pack(self):
        """Extend, return ECF player record and index data."""
        v = super().pack()
        index = v[1]
        index[filespec.ECFPLAYERCODE_FIELD_DEF] = [self.ECFcode]
        index[filespec.ECFPLAYERNAME_FIELD_DEF] = [self.ECFname]
        return v

    def pack_value(self, *a):
        """Override, return tuple of self attributes."""
        del a
        return repr(
            (
                self.ECFcode,
                self.ECFactive,
                self.ECFname,
                self.ECFclubcodes,
                self.ECFmerge,
            )
        )


class ECFrefDBrecordECFplayer(Record):
    """Player record from ECF."""

    def __init__(
        self, keyclass=ECFrefDBkeyECFplayer, valueclass=ECFrefDBvalueECFplayer
    ):
        """Customise Record by ECFrefDBkeyECFplayer, ECFrefDBvalueECFplayer."""
        super().__init__(keyclass, valueclass)


class ECFrefDBkeyECFdate(KeyData):
    """Primary key of ECF date record."""


class ECFrefDBvalueECFdate(Value):
    """ECF date data."""

    def __init__(self):
        """Extend Value with ECF transaction type and date."""
        super().__init__()
        self.ECFdate = None
        self.ECFtxntype = None
        self.ECFobjtype = None
        self.appliedECFdate = None

    def pack(self):
        """Extend, return ECF publication date record and index data."""
        v = super().pack()
        index = v[1]
        index[filespec.ECFDATE_FIELD_DEF] = [self.ECFdate]
        return v


class ECFrefDBrecordECFdate(Record):
    """ECF date record."""

    most_recent_club_master_file_date = None
    most_recent_player_master_file_date = None
    applied_club_master_file_date = None
    applied_player_master_file_date = None

    def __init__(
        self, keyclass=ECFrefDBkeyECFdate, valueclass=ECFrefDBvalueECFdate
    ):
        """Customise Record with ECFrefDBkeyECFdate, ECFrefDBvalueECFdate."""
        super().__init__(keyclass, valueclass)

    @staticmethod
    def get_most_recent_date(database, objtype, txntype=None):
        """Return the most recent known publication date for ECF data."""
        r = ECFrefDBrecordECFdate()
        mrd = None
        c = database.database_cursor(
            filespec.ECFTXN_FILE_DEF, filespec.ECFDATE_FIELD_DEF
        )
        try:
            d = c.last()
            while d:
                r.load_instance(
                    database,
                    filespec.ECFTXN_FILE_DEF,
                    filespec.ECFDATE_FIELD_DEF,
                    d,
                )
                if r.value.ECFobjtype == objtype:
                    if txntype is None:
                        mrd = r.value.ECFdate
                        break
                    if r.value.ECFtxntype == txntype:
                        mrd = r.value.ECFdate
                        break
                d = c.prev()
        finally:
            c.close()
        return mrd

    @staticmethod
    def records_exist(database):
        """Return True if ECF publication date records exist."""
        cursor = database.database_cursor(
            filespec.ECFTXN_FILE_DEF, filespec.ECFTXN_FIELD_DEF
        )
        try:
            return bool(cursor.first())
        finally:
            cursor.close()

    @staticmethod
    def set_most_recent_master_dates(database):
        """Calculate most recent publication dates for ECF master files."""
        r = ECFrefDBrecordECFdate()
        mrc = None
        mrp = None
        ac = None
        ap = None
        c = database.database_cursor(
            filespec.ECFTXN_FILE_DEF, filespec.ECFDATE_FIELD_DEF
        )
        try:
            d = c.last()
            while d:
                r.load_instance(
                    database,
                    filespec.ECFTXN_FILE_DEF,
                    filespec.ECFDATE_FIELD_DEF,
                    d,
                )
                if r.value.ECFtxntype == TXN_NEW:
                    if r.value.ECFobjtype == OBJTYPE_PLAYER:
                        if mrp is None:
                            mrp = r.value.ECFdate
                            ap = r.value.appliedECFdate
                    elif r.value.ECFobjtype == OBJTYPE_CLUB:
                        if mrc is None:
                            mrc = r.value.ECFdate
                    if mrc and mrp:
                        break
                d = c.prev()
        finally:
            c.close()
        ECFrefDBrecordECFdate.most_recent_club_master_file_date = mrc
        ECFrefDBrecordECFdate.most_recent_player_master_file_date = mrp
        ECFrefDBrecordECFdate.applied_club_master_file_date = ac
        ECFrefDBrecordECFdate.applied_player_master_file_date = ap


class ECFrefDBkeyEvent(KeyData):
    """Primary key of event."""


class ECFrefDBvalueEvent(ValueList):
    """Event data."""

    attributes = {
        "eventname": None,
        "eventcode": None,
        "eventstartdate": None,
        "eventenddate": None,
        "gradername": None,
        "graderemail": None,
        "graderaddress": None,
        "graderpostcode": None,
        "treasurername": None,
        "treasureraddress": None,
        "treasurerpostcode": None,
        "defaultcolour": None,
        "movesfirst": None,
        "moveslater": None,
        "minutesonly": None,
        "minutesfirst": None,
        "minuteslater": None,
        "minuteslast": None,
        "secondspermove": None,
        "adjudication": None,
        "informfide": None,
        "informchessmoves": None,
        "informgrandprix": None,
        "informeast": None,
        "informmidlands": None,
        "informnorth": None,
        "informsouth": None,
        "informwest": None,
        "submission": None,
    }
    _attribute_order = tuple(sorted(attributes.keys()))

    def get_ecf_event_identity(self):
        """Return tab separated ECF event identity."""
        return (self.eventname, self.eventstartdate, self.eventenddate)

    def pack(self):
        """Extend, return ECF event record and index data."""
        v = super().pack()
        index = v[1]
        index[filespec.ECFEVENTIDENTITY_FIELD_DEF] = [
            repr(self.get_ecf_event_identity())
        ]
        return v


class ECFrefDBrecordEvent(Record):
    """Event record."""

    def __init__(
        self, keyclass=ECFrefDBkeyEvent, valueclass=ECFrefDBvalueEvent
    ):
        """Customise Record with ECFrefDBkeyEvent and ECFrefDBvalueEvent."""
        super().__init__(keyclass, valueclass)


def get_ecf_player(database, key):
    """Return ECFrefDBrecordECFplayer instance for dbrecord[key]."""
    p = database.get_primary_record(filespec.ECFPLAYER_FILE_DEF, key)
    pr = ECFrefDBrecordECFplayer()
    pr.load_record(p)
    return pr


def get_ecf_player_for_grading_code(database, key):
    """Return ECFrefDBrecordECFplayer instance for key on index or None."""
    r = database.get_primary_record(
        filespec.ECFPLAYER_FILE_DEF,
        database.database_cursor(
            filespec.ECFPLAYER_FILE_DEF, filespec.ECFPLAYERCODE_FIELD_DEF
        ).get_unique_primary_for_index_key(
            database.encode_record_selector(key)
        ),
    )
    if r is not None:
        pr = ECFrefDBrecordECFplayer()
        pr.load_record(r)
        return pr
    return None


def get_ecf_club(database, key):
    """Return ECFrefDBrecordECFclub instance for dbrecord[key]."""
    c = database.get_primary_record(filespec.ECFCLUB_FILE_DEF, key)
    cr = ECFrefDBrecordECFclub()
    cr.load_record(c)
    return cr


def get_ecf_club_details(database, key):
    """Return ECFrefDBrecordECFclub instance for index key or null string."""
    pr = get_ecf_club_for_club_code(database, key)
    if pr is None:
        return ""
    if not pr.value.ECFactive:
        return ""
    return "\t".join((key, pr.value.ECFname))


def get_ecf_club_for_club_code(database, key):
    """Return ECFrefDBrecordECFclub instance for key on index or None."""
    r = database.get_primary_record(
        filespec.ECFCLUB_FILE_DEF,
        database.database_cursor(
            filespec.ECFCLUB_FILE_DEF, filespec.ECFCLUBCODE_FIELD_DEF
        ).get_unique_primary_for_index_key(
            database.encode_record_selector(key)
        ),
    )
    if r is not None:
        pr = ECFrefDBrecordECFclub()
        pr.load_record(r)
        return pr
    return None


def get_ecf_clubs_for_player(database, codelist):
    """Return (club name, ...) for most recent ECF transaction for player."""
    clubs = []
    for c in codelist:
        cr = get_ecf_club_for_club_code(database, c)
        if cr is None:
            clubs.append(c)
        elif cr.value.ECFactive:
            clubs.append(" ".join(cr.value.ECFname.split()))
        else:
            clubs.append(c)
    return sorted(clubs)


def get_ecf_event(value):
    """Return ECFrefDBrecordEvent instance for key on index or None."""
    if value:
        er = ECFrefDBrecordEvent()
        er.load_record(value)
    else:
        er = None
    return er


def get_merge_for_grading_code(database, key):
    """Return grading code with which key has been merged or key."""
    r = database.get_primary_record(
        filespec.ECFPLAYER_FILE_DEF,
        database.database_cursor(
            filespec.ECFPLAYER_FILE_DEF, filespec.ECFPLAYERCODE_FIELD_DEF
        ).get_unique_primary_for_index_key(
            database.encode_record_selector(key)
        ),
    )
    if r is not None:
        pr = ECFrefDBrecordECFplayer()
        pr.load_record(r)
        try:
            if pr.value.ECFmerge:
                if (
                    database.get_primary_record(
                        filespec.ECFPLAYER_FILE_DEF,
                        database.database_cursor(
                            filespec.ECFPLAYER_FILE_DEF,
                            filespec.ECFPLAYERCODE_FIELD_DEF,
                        ).get_unique_primary_for_index_key(
                            database.encode_record_selector(pr.value.ECFmerge)
                        ),
                    )
                    is not None
                ):
                    return pr.value.ECFmerge
        except:
            pass
    return key
