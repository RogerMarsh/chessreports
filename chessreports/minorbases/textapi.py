# textapi.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide read access to text files.

The database interface defined in the core.database.Database and
core.database.Cursor classes is used.

"""

import os
import os.path

# io may be used, for example, on csv files extracted from zip archives into
# memory rather than to a permanent file or database.
import io
import threading

# from ..core.database import DatabaseError, Database
# from ..core import cursor
# from ..core.constants import FILE, FOLDER, FIELDS
from solentware_base.core.constants import FILE, FOLDER


class TextapiError(Exception):  # DatabaseError):
    """Exception class for textapi module."""


class Textapi:  # (Database):
    """Implement Database API on a text file.

    The database is read only.
    textdb databases consist of one or more files each of which has zero
    fields defined. File names are unique. Each file contains zero or more
    records where each record contains one line of text.
    Records are identified by line number within a file. The lowest possible
    record number is zero.
    Applications are expected to store instances of one class on a file.
    Each instance is a line of text on a file.

    """

    def __init__(self, textdbfiles, textdbfolder):
        """Define database structure.

        textdb = {
            file:{
                folder:name,
                }, ...
            }

        dbasefolder = folder for files unless overridden in textdb

        """
        # The database definition from dbasefiles after validation
        self.textdbfiles = None

        # The folder from dbasefolder after validation
        self.textdbfolder = None

        # TextapiRoot objects for all textdb names.
        # {name:TextapiRoot instance, ...}
        self.main = {}

        files = {}
        pathnames = {}

        if textdbfolder is not False:
            try:
                textdbfolder = os.path.abspath(textdbfolder)
            except Exception as exc:
                msg = " ".join(
                    ["Main folder name", str(textdbfolder), "is not valid"]
                )
                raise TextapiError(msg) from exc

        for dd in textdbfiles:
            if len(dd) == 0:
                raise TextapiError("Zero length file name")

            try:
                folder = textdbfiles[dd].get(FOLDER, None)
            except Exception as exc:
                msg = " ".join(
                    [
                        "textdb file definition for",
                        repr(dd),
                        "must be a dictionary",
                    ]
                )
                raise TextapiError(msg) from exc

            if folder is None:
                folder = textdbfolder
            if textdbfolder is not False:
                try:
                    folder = os.path.abspath(folder)
                    fname = os.path.join(
                        folder, textdbfiles[dd].get(FILE, None)
                    )
                except Exception as exc:
                    msg = " ".join(["File name for", dd, "is invalid"])
                    raise TextapiError(msg) from exc
            else:
                fname = textdbfiles[dd].get(FILE, None)

            if fname in pathnames:
                msg = " ".join(
                    [
                        "File name",
                        fname,
                        "linked to",
                        pathnames[fname],
                        "cannot link to",
                        dd,
                    ]
                )
                raise TextapiError(msg)

            pathnames[fname] = dd
            files[dd] = {
                FILE: fname,
            }

            self.main[dd] = self.make_root(files[dd][FILE])

        self.textdbfiles = files
        self.textdbfolder = textdbfolder

    def close_context(self):
        """Close files."""
        for value in self.main.values():
            value.close()

    def exists(self, dbname, dummy):
        """Return True if dbname is one of the defined files.

        dummy is ignored.  It is present for compatibility with bsddb.

        """
        del dummy
        return dbname in self.main

    def database_cursor(self, dbname, dummy, keyrange=None, recordset=None):
        """Create a cursor on dbname.

        keyrange is an addition for DPT. It may yet be removed.
        dummy is ignored.  It is present for compatibility with others.
        recordset is ignored.  It is present for compatibility with others.

        """
        del dummy, keyrange, recordset
        if self.main[dbname].table_link is not None:
            return self.main[dbname].make_cursor()
        return None

    def get_database(self, dbname, dummy):
        """Return file for dbname.

        dummy is ignored.  It is present for compatibility with bsddb.

        """
        del dummy
        return self.main[dbname].table_link

    def get_primary_record(self, dbname, record):
        """Return record.

        dbname is ignored.  It is present for compatibility with bsddb.

        """
        del dbname
        return record

    def is_primary(self, dbname, dummy):
        """Return True.

        dbname and dummy are ignored.  They are present for compatibility
        with bsddb.

        """
        del dbname, dummy
        return True

    def is_primary_recno(self, dbname):
        """Return True.

        dbname is ignored.  It is present for compatibility with bsddb.

        """
        del dbname
        return True

    def is_recno(self, dbname, dummy):
        """Return True.

        dbname and dummy are ignored.  They are present for compatibility
        with bsddb.

        """
        del dbname, dummy
        return True

    def open_context(self):
        """Open all files."""
        for key, value in self.main.items():
            value.open_root()
            if value.table_link is None:
                for cvalue in self.main.values():
                    cvalue.close()
                raise TextapiError(" ".join(["Open file", repr(key)]))

    def decode_as_primary_key(self, dbname, srkey):
        """Return srkey.

        dbname is ignored.  It is present for compatibility with bsddb.

        """
        del dbname
        return srkey

    def make_root(self, filename):
        """Return TextapiRoot instance for filename."""
        return TextapiRoot(filename)


class TextapiRoot:
    """Provide record access to a text file in bsddb style.

    The cursor instance returned by Cursor() duplicates many methods in
    this class.  The bsddb interface provides similar methods on the
    underlying database and via cursors on that database.  In that
    context the behaviour can be very diferrent.

    """

    def __init__(self, filename):
        """Initialise for text file "filename" in closed state."""
        self._localdata = threading.local()
        self._lock_text = threading.Lock()
        with self._lock_text:
            self.filename = filename
            self._clientcursors = {}
            # Avoid a host of pylint W0201 attribute-defined-outside-init
            # reports by not calling _set_closed_state to do this
            # initialization.
            # self._set_closed_state()
            self._table_link = None
            self.textlines = None
            self.record_count = None
            self._localdata.record_number = None
            self._localdata.record_select = None
            # self._clientcursors.clear()

    def __del__(self):
        """Close text file when instance destroyed."""
        self.close()

    @property
    def table_link(self):
        """Reurn the file or IO bytes object."""
        return self._table_link

    def close(self):
        """Close text file."""
        with self._lock_text:
            try:
                try:
                    self._table_link.close()
                except:
                    pass
            finally:
                self._set_closed_state()

    def make_cursor(self):
        """Create and return a record (line) cursor on the text file."""
        with self._lock_text:
            if self._table_link is None:
                return None
            c = Cursor(self)
            self._clientcursors[c] = True
            return c

    def close_cursor(self, cursor):
        """Close a cursor in clientcursors."""
        if cursor in self._clientcursors:
            del self._clientcursors[cursor]

    def open_root(self):
        """Open text file and extract lines as records."""
        with self._lock_text:
            try:
                if isinstance(self.filename, io.BytesIO):
                    self._table_link = self.filename
                else:
                    self._table_link = open(self.filename, "rb")
                self.textlines = self._table_link.read().splitlines()
                self.record_count = len(self.textlines)
                self._localdata.record_number = None
                self._localdata.record_select = None
            except:
                self._table_link = None

    def first(self):
        """Return first record."""
        value = self._first_record()
        if value is not None:
            return (self._localdata.record_select, value)
        return None

    def last(self):
        """Return last record."""
        value = self._last_record()
        if value is not None:
            return (self._localdata.record_select, value)
        return None

    def nearest(self, current):
        """Return nearest record."""
        self._set_record_number(current)
        value = self._get_record()
        if value is not None:
            return (self._localdata.record_select, value)
        return None

    def next(self, current):
        """Return next record."""
        self._set_record_number(current)
        value = self._next_record()
        if value is not None:
            return (self._localdata.record_select, value)
        return None

    def prior(self, current):
        """Return prior record."""
        self._set_record_number(current)
        value = self._prior_record()
        if value is not None:
            return (self._localdata.record_select, value)
        return None

    def setat(self, current):
        """Return current record."""
        self._set_record_number(current)
        value = self._get_record()
        if value is not None:
            return (self._localdata.record_select, value)
        return None

    def _set_closed_state(self):
        self._table_link = None
        self.textlines = None
        self.record_count = None
        self._localdata.record_number = None
        self._localdata.record_select = None
        self._clientcursors.clear()

    def _first_record(self):
        """Position at and return first line of text."""
        self._select_first()
        return self._get_record()

    def _get_record(self):
        """Return selected line of text."""
        with self._lock_text:
            if self._table_link is None:
                return None
            if self._localdata.record_select < 0:
                self._localdata.record_select = -1
                return None
            if self._localdata.record_select >= self.record_count:
                self._localdata.record_select = self.record_count
                return None
            self._localdata.record_number = self._localdata.record_select
            return self.textlines[self._localdata.record_number]

    def _last_record(self):
        """Position at and return last line of text."""
        self._select_last()
        return self._get_record()

    def _next_record(self):
        """Position at and return next line of text."""
        self._select_next()
        return self._get_record()

    def _prior_record(self):
        """Position at and return prior line of text."""
        self._select_prior()
        return self._get_record()

    def _select_first(self):
        """Set record selection cursor at first record."""
        self._localdata.record_select = 0
        return self._localdata.record_select

    def _select_last(self):
        """Set record selection cursor at last record."""
        self._localdata.record_select = self.record_count - 1
        return self._localdata.record_select

    def _select_next(self):
        """Set record selection cursor at next record."""
        self._localdata.record_select = self._localdata.record_number + 1
        return self._localdata.record_select

    def _select_prior(self):
        """Set record selection cursor at prior record."""
        self._localdata.record_select = self._localdata.record_number - 1
        return self._localdata.record_select

    def _set_record_number(self, number):
        """Set record selection cursor at the specified record."""
        if not isinstance(number, int):
            self._localdata.record_select = -1
        elif number > self.record_count:
            self._localdata.record_select = self.record_count
        elif number < 0:
            self._localdata.record_select = -1
        else:
            self._localdata.record_select = number


class Cursor:  # (cursor.Cursor):
    """Define cursor implemented using the Berkeley DB cursor methods."""

    def __init__(self, dbobject, **kargs):
        """Cursor emulates parts of a bsddb3 cursor.

        dbobject - An OS file instance.
        kargs - absorb argunents relevant to other database engines.

        """
        del kargs
        super().__init__()  # dbobject)
        self._cursor = _CursorText(dbobject)

    def first(self):
        """First record taking partial key into account."""
        return self._get_record(self._cursor.first())

    def get_partial(self):
        """Return None.  Partial key not relevant.

        The _partial_key attribute is ignored.

        """
        return None

    def last(self):
        """Last record taking partial key into account."""
        return self._get_record(self._cursor.last())

    def set_partial_key(self, partial):
        """Do nothing.  Partial key not relevant.

        The _partial_key attribute is ignored.

        """

    def _get_record(self, record):
        """Return record if key matches partial key (if any)."""
        return record

    def nearest(self, key):
        """Nearest record taking partial key into account."""
        return self._get_record(self._cursor.set_range(key))

    def next(self):
        """Next record taking partial key into account."""
        return self._get_record(self._cursor.next())

    def prev(self):
        """Previous record taking partial key into account."""
        return self._get_record(self._cursor.prev())

    def setat(self, record):
        """Position cursor at record taking partial key into account."""
        return self._get_record(self._cursor.set(record[0]))

    def count_records(self):
        """Return record count or None if cursor is not usable."""
        # if not self.is_cursor_open():
        if self._cursor is None:
            return None
        # return self.cursor_count()
        return self._cursor.record_count

    def get_position_of_record(self, record=None):
        """Return position of record in file or 0 (zero)."""
        if record is None:
            return 0
        start = self.first
        step = self.next
        position = 0
        k = record[0]
        r = start()
        while r:
            if r[0] >= k:
                break
            position += 1
            r = step()
        return position

    def get_record_at_position(self, position=None):
        """Return record for positionth record in file or None."""
        if position is None:
            return None
        if position < 0:
            start = self.last
            step = self.prev
            position = -1 - position
        else:
            start = self.first
            step = self.next
        count = 0
        r = start()
        while r:
            count += 1
            if count > position:
                break
            r = step()
        if r is not None:
            return r
        return None


class _CursorText:
    """Define a text file cursor.

    Wrap the TextapiRoot methods in corresponding cursor method names.
    The methods with all lower case names emulate the bsddb cursor
    methods.

    """

    def __init__(self, dbobject):
        self._dbobject = dbobject
        self._current = -1

    def __del__(self):
        self.close()

    @property
    def record_count(self):
        """Return record count of self._dboject."""
        return self._dbobject.record_count

    def close(self):
        """Close cursor."""
        try:
            self._dbobject.close_cursor(self)
        finally:
            self._set_closed_state()

    def current(self):
        """Read current record."""
        r = self._dbobject.setat(self._current)
        if r:
            self._current = r[0]
            return r
        return None

    def first(self):
        """Read first record."""
        r = self._dbobject.first()
        if r:
            self._current = r[0]
            return r
        return None

    def last(self):
        """Read last record."""
        r = self._dbobject.last()
        if r:
            self._current = r[0]
            return r
        return None

    def next(self):
        """Read next record."""
        r = self._dbobject.next(self._current)
        if r:
            self._current = r[0]
            return r
        return None

    def prev(self):
        """Read prior record."""
        r = self._dbobject.prior(self._current)
        if r:
            self._current = r[0]
            return r
        return None

    def set(self, key):
        """Read current record."""
        r = self._dbobject.setat(key)
        if r:
            self._current = r[0]
            return r
        return None

    def set_range(self, key):
        """Read nearest record."""
        r = self._dbobject.nearest(key)
        if r:
            self._current = r[0]
            return r
        return None

    def set_both(self, key, value):
        """Read nearest record."""
        del value
        r = self._dbobject.nearest(key)
        if r:
            self._current = r[0]
            return r
        return None

    def _set_closed_state(self):
        self._dbobject = None
        self._current = None
