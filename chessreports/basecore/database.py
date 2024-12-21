# database.py
# Copyright 2019 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ChessReports database methods common to all database engine interfaces."""

import os
import shutil

from .. import APPLICATION_NAME, ERROR_LOG


# A solentware_base.core Database class defining the members which get
# E1101 is expected lower in MRO.  Several modules define these items.
class Database:
    """Provide methods common to all database engine interfaces."""

    def open_database(self, files=None):
        """Return '' to fit behaviour of dpt version of this method."""
        # See class definition comment.
        # pylint: disable-next=no-member.
        super().open_database(files=files)
        return ""

    def _delete_database_names(self):
        """Return tuple of filenames to delete from database directory.

        Subclasses should override this method to delete the relevant files.
        """

    def delete_database(self):
        """Delete results database and return message for items not deleted."""
        # See class definition comment.
        # pylint: disable-next=no-member.
        home_directory = self.home_directory
        listnames = set(n for n in os.listdir(home_directory))
        homenames = set(
            n
            for n in self._delete_database_names()
            if os.path.basename(n) in listnames
        )
        if ERROR_LOG in listnames:
            homenames.add(os.path.join(home_directory, ERROR_LOG))
        if len(listnames - set(os.path.basename(h) for h in homenames)):
            message = "".join(
                (
                    "There is at least one file or folder in\n\n",
                    home_directory,
                    "\n\nwhich may not be part of the database.  These items ",
                    "have not been deleted by ",
                    APPLICATION_NAME,
                    ".",
                )
            )
        else:
            message = None
        # See class definition comment.
        # pylint: disable-next=no-member.
        self.close_database()
        for pathname in homenames:
            if os.path.isdir(pathname):
                shutil.rmtree(pathname, ignore_errors=True)
            else:
                os.remove(pathname)
        try:
            os.rmdir(home_directory)
        except FileNotFoundError as exc:
            message = str(exc)
        except OSError as exc:
            if message:
                message = "\n\n".join((str(exc), message))
            else:
                message = str(exc)
        return message

    def strify(self, value):
        """Tranform a value from an ECF DbaseIII file to str.

        Assume iso-8859-1 encoding for value.

        """
        return value.decode("iso-8859-1")

    # Not clear why keyify is necessary.  See version in db.resultsdatabase.
    def keyify(self, value):
        """Tranform a value from ECF DbaseIII file for database key search."""
        return self.strify(value)

    # Not clear why keybyteify is necessary except it is same as for keyify.
    # See version in db.resultsdatabase.
    def keybyteify(self, value):
        """Tranform a value from ECF json download for database key search."""
        return value
