# control.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Control panel class.

Open and close databases and import and export data functions are available
on this panel.

"""

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os
import zipfile
import io
import email
import base64
import json
import urllib.request
import datetime

try:
    import tnefparse
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    tnefparse = None

from solentware_misc.gui import dialogue
from solentware_misc.core.getconfigurationitem import get_configuration_item

from .feedback_monthly import show_ecf_results_feedback_monthly_tab
from . import ecfdownload
from .. import control_database
from ...minorbases.dbaseapi import DBaseapiError
from ...core.filespec import (
    ECFPLAYER_FILE_DEF,
    ECFCLUB_FILE_DEF,
    ECFTXN_FILE_DEF,
    MAPECFPLAYER_FILE_DEF,
)
from ...core import constants
from ...core import configuration
from ...core.ecf import ecfdataimport
from ...core.ecf import ecfclubdb
from ...core.ecf import ecfplayerdb


class Control(control_database.Control):
    """The Control panel for a Results database."""

    btn_ecfresultsfeedback = "control_feedback"
    btn_ecfresultsfeedbackmonthly = "control_feedback_monthly"
    _btn_ecfmasterfile = "control_master_file"
    _btn_quitecfzippedfiles = "control_quit"
    btn_copyecfmasterplayer = "control_copy_master_player"
    btn_copyecfmasterclub = "control_copy_master_club"
    btn_playersdownload = "control_players_download"
    btn_clubsdownload = "control_clubs_download"

    # pylint W0102 dangerous-default-value.
    # cnf used as tkinter.Frame argument, which defaults to {}.
    def __init__(self, parent=None, cnf={}, **kargs):
        """Extend and define the results database control panel."""
        super().__init__(parent=parent, cnf=cnf, **kargs)

        self.ecf_reference_file = None
        self._ecf_reference_widget = None
        self.ecfclubfile = None
        self.ecfplayerfile = None
        self.ecfdatecontrol = None

    def close_update_resources(self):
        """Close any open files containing master data from ECF."""
        if self.ecfplayerfile is not None:
            self.ecfplayerfile.close_context()
            self._delete_dbase_files(self.ecfplayerfile)
            self.ecfplayerfile = None
        if self.ecfclubfile is not None:
            self.ecfclubfile.close_context()
            self._delete_dbase_files(self.ecfclubfile)
            self.ecfclubfile = None
        if self.ecfdatecontrol is not None:
            self.ecfdatecontrol.destroy()
            self.ecfdatecontrol = None

    def describe_buttons(self):
        """Define all action buttons that may appear on Control page."""
        super().describe_buttons()
        self.define_button(
            self.btn_ecfresultsfeedback,
            text="ECF Grading Feedback",
            tooltip=(
                "Display a feedback email for a results submission to ECF."
            ),
            underline=4,
            switchpanel=True,
            command=self.on_ecf_results_feedback,
        )
        self.define_button(
            self.btn_ecfresultsfeedbackmonthly,
            text="ECF Rating Feedback",
            tooltip="Display a feedback email for a results upload to ECF.",
            underline=18,
            switchpanel=True,
            command=self.on_ecf_results_feedback_monthly,
        )
        self.define_button(
            self.btn_playersdownload,
            text="Rated Players Download",
            tooltip="Download list of rated players from ECF website",
            underline=7,
            switchpanel=True,
            command=self.on_ecf_players_download,
        )
        self.define_button(
            self.btn_clubsdownload,
            text="Active Clubs Download",
            tooltip="Download list of active clubs from ECF website",
            underline=4,
            switchpanel=True,
            command=self.on_ecf_clubs_download,
        )
        self.define_button(
            self._btn_ecfmasterfile,
            text="ECF Master File",
            tooltip="Open a zipped ECF Master file.",
            underline=4,
            command=self.on_ecf_master_file,
        )
        self.define_button(
            self._btn_quitecfzippedfiles,
            text="Close File List",
            tooltip="Close the list of files in the zipped archive.",
            underline=1,
            command=self.on_quit_ecf_zipped_files,
        )
        self.define_button(
            self.btn_copyecfmasterplayer,
            text="Show Master File",
            tooltip="Build new Master file for players.",
            underline=3,
            switchpanel=True,
            command=self.on_copy_ecf_master_player,
        )
        self.define_button(
            self.btn_copyecfmasterclub,
            text="Show Master Club File",
            tooltip="Build new Master file for clubs.",
            underline=1,
            switchpanel=True,
            command=self.on_copy_ecf_master_club,
        )

    def on_ecf_results_feedback(self, event=None):
        """Do ECF feedback actions."""
        del event
        conf = configuration.Configuration()
        filepath = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title="Open ECF feedback email or attachment",
            # defaultextension='.txt',
            # filetypes=(('ECF feedback', '*.txt'),),
            initialdir=conf.get_configuration_value(
                constants.RECENT_FEEDBACK_EMAIL
            ),
        )
        if not filepath:
            self.inhibit_context_switch(self.btn_ecfresultsfeedback)
            return
        conf.set_configuration_value(
            constants.RECENT_FEEDBACK_EMAIL,
            conf.convert_home_directory_to_tilde(os.path.dirname(filepath)),
        )
        try:
            with open(filepath, "rb") as feedbackfile:
                self.get_appsys().set_kwargs_for_next_tabclass_call(
                    {"datafile": (filepath, _get_feedback_text(feedbackfile))}
                )
        except:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "File\n",
                        os.path.split(feedbackfile)[-1],
                        "\ndoes not exist",
                    )
                ),
                title=" ".join(["Open ECF feedback email or attachment"]),
            )
            return

    def on_ecf_results_feedback_monthly(self, event=None):
        """Do ECF feedback actions."""
        del event
        show_ecf_results_feedback_monthly_tab(
            self, self.btn_ecfresultsfeedbackmonthly
        )

    def _ecf_download(self, name, button, default_url, contexts, structure):
        """Do download actions for rated players or active clubs.

        The process is identical so provide arguments to fit each case.

        """
        name_title = name.title()
        title = " ".join(("Get", name_title))
        dlg = ecfdownload.ECFDownloadDialogue(
            parent=self.appsys,
            # title,
            text=title,  # name,
            scroll=False,
            height=7,
            width=60,
            wrap=tkinter.WORD,
        )
        dlg.go()
        # Method is defined by setattr in a superclass.
        # pylint: disable-next=no-member
        if dlg.cancel_pressed():
            self.inhibit_context_switch(button)
            return
        # Method is defined by setattr in a superclass.
        # pylint: disable-next=no-member
        if dlg.download_pressed():
            conf = configuration
            dialogue_result = dialogue.ModalEntryApply(
                parent=self.appsys,
                title=title,
                body=(
                    (
                        "URL",
                        get_configuration_item(
                            conf.Configuration().get_configuration_file_name(),
                            default_url,
                            constants.DEFAULT_URLS,
                        ),
                        None,
                        False,
                    ),
                ),
            ).result
            if dialogue_result is None:
                self.inhibit_context_switch(button)
                return
            urlname = dialogue_result["URL"]
            try:
                with urllib.request.urlopen(urlname) as url:
                    try:
                        urldata = url.read()
                    except Exception as exc:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            title=title,
                            message="".join(
                                (
                                    "Exception raised trying to read URL\n\n",
                                    str(exc),
                                )
                            ),
                        )
                        self.inhibit_context_switch(button)
                        return
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=title,
                    message="".join(
                        ("Exception raised trying to open URL\n\n", str(exc))
                    ),
                )
                self.inhibit_context_switch(button)
                return
            try:
                data = structure(json.loads(urldata))
                self.get_appsys().set_kwargs_for_next_tabclass_call(
                    {
                        "datafile": (
                            urlname,
                            str(datetime.date.today()),
                            data,
                        ),
                        "closecontexts": contexts,
                    }
                )
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=title,
                    message="".join(
                        (
                            name.join(
                                (
                                    "Exception raised trying to extract ",
                                    " from URL\n\n",
                                )
                            ),
                            str(exc),
                        )
                    ),
                )
                self.inhibit_context_switch(button)
                return
            return
        # Method is defined by setattr in a superclass.
        # pylint: disable-next=no-member
        if dlg.extract_pressed():
            open_title = " ".join(("Open downloaded", name_title))
            dlg = tkinter.filedialog.askopenfilename(
                parent=self.get_widget(), title=open_title, initialdir="~"
            )
            if not dlg:
                self.inhibit_context_switch(button)
                return
            try:
                with open(dlg, encoding="utf8").read() as urldata:
                    try:
                        data = structure(json.loads(urldata))
                        self.get_appsys().set_kwargs_for_next_tabclass_call(
                            {
                                "datafile": (
                                    dlg,
                                    str(datetime.date.today()),
                                    data,
                                ),
                                "closecontexts": contexts,
                            }
                        )
                    except Exception as exc:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            title=open_title,
                            message="".join(
                                (
                                    "".join(
                                        (
                                            "Exception raised trying to ",
                                            "extract ",
                                            name,
                                            " from URL\n\n",
                                        )
                                    ),
                                    str(exc),
                                )
                            ),
                        )
                        self.inhibit_context_switch(button)
                        return
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=open_title,
                    message="".join(
                        ("Exception raised trying to read File\n\n", str(exc))
                    ),
                )
                self.inhibit_context_switch(button)
                return

    def _ecf_players_structure(self, data):
        """Validate json player data structure.

        The set of column names changed once, I think, when the blitz
        categories promised were added.

        """
        if set(data.keys()) == constants.PLAYERS_RATINGS_KEYS:
            column_names = tuple(data[constants.P_R_COLUMN_NAMES])
            for prcn in (
                constants.PLAYERS_RATINGS_COLUMN_NAMES_2022_10,
                constants.PLAYERS_RATINGS_COLUMN_NAMES_ORIGINAL,
            ):
                if column_names == prcn:
                    return data
        raise RuntimeError(
            "".join(
                (
                    "Downloaded data not in expected format for rated ",
                    "players.\n\nHas the format been changed?",
                )
            )
        )

    def _ecf_clubs_structure(self, data):
        """Validate json club data structure."""
        if set(data.keys()) == constants.ACTIVE_CLUBS_KEYS:
            return data
        raise RuntimeError(
            "".join(
                (
                    "Downloaded data not in expected format for active clubs.",
                    "\n\nHas the format been changed?",
                )
            )
        )

    def on_ecf_players_download(self, event=None):
        """Do list of rated players download actions."""
        del event
        self._ecf_download(
            "rated players",
            self.btn_playersdownload,
            constants.PLAYERS_RATINGS_URL,
            (ECFPLAYER_FILE_DEF, ECFTXN_FILE_DEF, MAPECFPLAYER_FILE_DEF),
            self._ecf_players_structure,
        )

    def on_ecf_clubs_download(self, event=None):
        """Do ECF clubs download actions."""
        del event
        self._ecf_download(
            "active clubs",
            self.btn_clubsdownload,
            constants.ACTIVE_CLUBS_URL,
            (ECFCLUB_FILE_DEF, ECFTXN_FILE_DEF),
            self._ecf_clubs_structure,
        )

    def on_quit_ecf_zipped_files(self, event=None):
        """Do quit import ECF Master File actions."""
        del event
        self._ecf_reference_widget.destroy()
        self._ecf_reference_widget = None
        self.datafilepath.configure(
            text=os.path.dirname(self.datafilepath.cget("text"))
        )
        self.ecf_reference_file = None
        self.show_buttons_for_open_database()
        self.create_buttons()

    def on_copy_ecf_master_player(self, event=None):
        """Do copy ECF Master File (players) actions."""
        del event
        dbspec = self._get_memory_dbase3_from_zipfile(ecfplayerdb.ECFplayersDB)
        if dbspec is None:
            self.inhibit_context_switch(self.btn_copyecfmasterplayer)
            return
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            {
                "datafilespec": (
                    dbspec[0],
                    ecfplayerdb.PLAYERS,
                    ecfplayerdb.PLAYERS,
                ),
                "datafilename": dbspec[1],
                "closecontexts": (
                    ECFPLAYER_FILE_DEF,
                    ECFTXN_FILE_DEF,
                    MAPECFPLAYER_FILE_DEF,
                ),
                "tabtitle": "Master List",
                "copymethod": ecfdataimport.copy_ecf_players_post_2011_rules,
            }
        )

    def on_copy_ecf_master_club(self, event=None):
        """Do copy ECF club file actions."""
        del event
        dbspec = self._get_memory_dbase3_from_zipfile(ecfclubdb.ECFclubsDB)
        if dbspec is None:
            self.inhibit_context_switch(self.btn_copyecfmasterclub)
            return
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            {
                "datafilespec": (dbspec[0], ecfclubdb.CLUBS, ecfclubdb.CLUBS),
                "datafilename": dbspec[1],
                "closecontexts": (ECFCLUB_FILE_DEF, ECFTXN_FILE_DEF),
                "tabtitle": "Club List",
                "copymethod": ecfdataimport.copy_ecf_clubs_post_2011_rules,
            }
        )

    def on_ecf_master_file(self, event=None):
        """Do unzip ECF master file actions."""
        del event
        if self.display_ecf_zipped_file_contents():
            self.show_buttons_for_ecf_master_file()
            self.create_buttons()

    def display_ecf_zipped_file_contents(self):
        """Display ECF master data with date for confirmation of update."""
        conf = configuration.Configuration()
        filepath = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title="Open ECF data file",
            defaultextension=".zip",
            filetypes=(("ECF master lists", "*.zip"),),
            initialdir=conf.get_configuration_value(
                constants.RECENT_MASTERFILE
            ),
        )
        if not filepath:
            return None
        conf.set_configuration_value(
            constants.RECENT_MASTERFILE,
            conf.convert_home_directory_to_tilde(os.path.dirname(filepath)),
        )

        with zipfile.ZipFile(filepath, "r") as ziparchive:
            namelist = ziparchive.namelist()
            if len(namelist):
                frame = tkinter.Frame(master=self.get_widget())
                listbox = tkinter.Listbox(master=frame)
                yscrollbar = tkinter.Scrollbar(
                    master=frame,
                    orient=tkinter.VERTICAL,
                    command=listbox.yview,
                )
                xscrollbar = tkinter.Scrollbar(
                    master=frame,
                    orient=tkinter.HORIZONTAL,
                    command=listbox.xview,
                )
                listbox.configure(
                    yscrollcommand=yscrollbar.set,
                    xscrollcommand=xscrollbar.set,
                )
                yscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
                xscrollbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
                listbox.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
                frame.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
                listbox.insert(tkinter.END, *sorted(namelist))
                self.datafilepath.configure(text=filepath)
                self.ecf_reference_file = listbox
                self._ecf_reference_widget = frame
                return True
            return None

    def open_file_from_ecf_zipped_master_file(
        self, dbdefinition, dbset, dbname, archive, element
    ):
        """Display ECF master data with date for confirmation of update."""
        del dbset, dbname
        memory_file = None
        with zipfile.ZipFile(archive, "r") as ziparchive:
            for za in ziparchive.namelist():
                if za == element:
                    memory_file = io.BytesIO(ziparchive.read(za))
                    break

        ecffile = dbdefinition(memory_file)
        try:
            ecffile.open_context()
            return (ecffile, (archive, element))
        except DBaseapiError as msg:
            try:
                ecffile.close_context()
            except:
                pass
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=str(msg),
                title=" ".join(["Open ECF player file"]),
            )
        except Exception as msg:
            try:
                ecffile.close_context()
            except:
                pass
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join([str(Exception), str(msg)]),
                title=" ".join(["Open ECF player file"]),
            )
        return None

    def show_buttons_for_ecf_master_file(self):
        """Show buttons for actions allowed importing new ECF player data."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self.btn_closedatabase,
                self._btn_quitecfzippedfiles,
                self.btn_copyecfmasterclub,
                self.btn_copyecfmasterplayer,
            )
        )

    def show_buttons_for_open_database(self):
        """Show buttons for actions allowed when database is open."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self.btn_closedatabase,
                self.btn_ecfresultsfeedbackmonthly,
                self.btn_ecfresultsfeedback,
                self.btn_playersdownload,
                self.btn_clubsdownload,
                self._btn_ecfmasterfile,
                self.btn_importevents,
            )
        )

    def _delete_dbase_files(self, dbaseobject):
        """Delete DBF files extracted from ECF master file ZIP file."""
        if not dbaseobject:
            return False

        for obj in dbaseobject.dbasefiles.values():
            if os.path.isfile(obj.file_name):
                try:
                    os.remove(obj.file_name)
                except:
                    pass
        return None

    def _get_memory_dbase3_from_zipfile(self, dbdefinition):
        """Create 'in-memory' dBaseIII file from zipped file."""
        selection = self.ecf_reference_file.curselection()
        if not selection:
            return None
        selected_file = self.datafilepath.cget("text")
        selected_element = self.ecf_reference_file.get(selection)
        return self.open_file_from_ecf_zipped_master_file(
            dbdefinition,
            None,
            None,
            selected_file,
            selected_element,
        )


def _get_feedback_text(file):
    """Return feedback text from open file.

    Required text is assumed to be in 'text/plain' parts of message, where the
    'text/plain' may be inside an 'application/ms-tnef' attachment.

    """
    m = email.message_from_binary_file(file)

    # Assume file is a saved attachment file when there are no headers.
    if not m.keys():
        file.seek(0)
        return [line.rstrip() for line in file.readlines()]

    text = []
    for part in m.walk():
        ct = part.get_content_type()
        if ct == "text/plain":
            text.extend(
                [
                    line.rstrip()
                    for line in part.get_payload().encode("utf8").split(b"\n")
                ]
            )
        elif ct == "application/ms-tnef":
            if not tnefparse:
                text.append(
                    b"Cannot process feedback: tnefparse is not installed."
                )
                continue

            # Assume the attachments are txt.
            # Feedback attachments have always been txt files: until December
            # 2016 these were not wrapped inside an application/ms-tnef
            # attachment.
            tnef = tnefparse.TNEF(base64.b64decode(part.get_payload()))
            for attachment in tnef.attachments:
                text.extend(
                    [line.rstrip() for line in attachment.data.split(b"\n")]
                )

    return text
