# feedback.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results feedback database update class.

Display a feedback document from ECF alongside the grading code updates
for new players deduced from the content.  The selected updates are applied
to the database.

"""

import tkinter

from solentware_misc.gui import panel
from solentware_misc.gui import textreadonly
from solentware_misc.gui import tasklog

from ...core import resultsrecord
from ...core import filespec
from ...core import constants
from ...core.ecf import ecfrecord
from ...core.ecf import ecfmaprecord

_SUBLINE = "Line "
_PIN_LINE = "New Player - Pin "
_NEWCODE_LINE = "New code generated - "
_USECODE_LINE = "Code to be used is "
_MERGECODE_LINE = ": Please note that the ECF Code supplied ("
_CLUB_LINE = ": New Club supplied ("


class Feedback(panel.PlainPanel):
    """The Feedback panel for a Results database."""

    btn_closefeedback = "feedback_close"
    _btn_applyfeedback = "feedback_apply"

    # pylint W0102 dangerous-default-value.
    # cnf used as tkinter.Frame argument, which defaults to {}.
    def __init__(self, parent=None, datafile=None, cnf={}, **kargs):
        """Extend and define the results database feedback panel."""
        super().__init__(parent=parent, cnf=cnf, **kargs)

        datafilename, feedbacklines = datafile

        self.show_buttons_for_start_import()
        self.create_buttons()

        self.datafilepath = tkinter.Label(
            master=self.get_widget(), text=datafilename
        )
        self.datafilepath.pack(side=tkinter.TOP, fill=tkinter.X)

        pw = tkinter.PanedWindow(
            self.get_widget(),
            opaqueresize=tkinter.FALSE,
            orient=tkinter.VERTICAL,
        )
        pw.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE)

        self.allowapplycodes = None
        self.newcodesapply = None
        toppane = tkinter.PanedWindow(
            master=pw, opaqueresize=tkinter.FALSE, orient=tkinter.HORIZONTAL
        )
        feedbackpane = tkinter.PanedWindow(
            master=toppane, opaqueresize=tkinter.FALSE, orient=tkinter.VERTICAL
        )
        applypane = tkinter.PanedWindow(
            master=toppane, opaqueresize=tkinter.FALSE, orient=tkinter.VERTICAL
        )
        fbf, feedbackctrl = textreadonly.make_scrolling_text_readonly(
            master=feedbackpane, wrap=tkinter.WORD, undo=tkinter.FALSE
        )
        af, self.applyctrl = textreadonly.make_scrolling_text_readonly(
            master=applypane, wrap=tkinter.WORD, undo=tkinter.FALSE
        )
        applypane.add(af)
        feedbackpane.add(fbf)
        toppane.add(feedbackpane)
        toppane.add(applypane)
        toppane.paneconfigure(feedbackpane, stretch=tkinter.FIRST)

        rf = tkinter.Frame(master=pw)
        self.tasklog = tasklog.TaskLog(
            # threadqueue=self.get_appsys().get_thread_queue(),
            logwidget=tasklog.LogText(
                master=rf, cnf={"wrap": tkinter.WORD, "undo": tkinter.FALSE}
            ),
        )
        pw.add(toppane)
        pw.add(rf)
        pw.paneconfigure(toppane, stretch=tkinter.FIRST)
        pw.paneconfigure(rf, stretch="never")

        feedbackctrl.insert(tkinter.END, b"\n".join(feedbacklines))
        self.applyctrl.insert(
            tkinter.END,
            self.extract_and_report_new_grading_codes(feedbacklines),
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """

    def apply_new_grading_codes(self, *args, **kargs):
        """Apply new grading codes from feedback and return report.

        args and kargs soak up arguments set by threading or multiprocessing
        when running this method.

        """
        del args, kargs
        if not self.allowapplycodes:
            return False

        def new_club():
            record = ecfrecord.ECFrefDBrecordECFclub()
            record.key.recno = None
            record.value.ECFcode = fbplayer[constants.CLUB_CODE]
            record.value.ECFname = fbplayer[constants.CLUB]
            record.value.ECFactive = False
            record.put_record(database, filespec.ECFCLUB_FILE_DEF)
            applycodesreport.append(
                (
                    fbplayer[constants.CLUB_CODE],
                    fbplayer[constants.CLUB],
                    "added as feedback update to club list",
                )
            )

        def new_ecf_player(gcode):
            record = ecfrecord.ECFrefDBrecordECFplayer()
            record.key.recno = None
            record.value.ECFcode = gcode
            record.value.ECFname = fbplayer[constants.NAME]
            record.value.ECFactive = False
            if fbplayer[_MERGECODE_LINE]:
                record.value.ECFmerge = fbplayer[_MERGECODE_LINE]
            record.put_record(database, filespec.ECFPLAYER_FILE_DEF)
            applycodesreport.append(
                (
                    gcode,
                    fbplayer[constants.NAME],
                    "added as feedback update to master list",
                )
            )
            # Added to avoid pylint E1111 report (assignment-from-no-return).
            # Gets pylint R1711 report (useless-return) and E1128 when called.
            # Providing an alternative return value above avoids both R1711
            # and E1128 when function is called 'f = new_ecf_player(1)'.
            return None

        def update_ecf_player():
            # Unmerge not done by feedback merge line.
            # Currently wait for full Masterlist, but does absence of merge
            # line imply break merge if it does not exist?
            if not fbplayer[_MERGECODE_LINE]:
                return False

            if fbplayer[_MERGECODE_LINE] == ecfplayer.value.ECFmerge:
                return None
            if ecfplayer.value.ECFmerge:
                repmerge = " ".join(
                    ("replacing noted merge into", ecfplayer.value.ECFmerge)
                )
            else:
                repmerge = ""
            ecfplayerclone = ecfplayer.clone()
            ecfplayerclone.value.ECFmerge = fbplayer[_MERGECODE_LINE]
            ecfplayerclone.value.ECFactive = not bool(
                fbplayer[_MERGECODE_LINE]
            )
            ecfplayer.edit_record(
                database,
                filespec.ECFPLAYER_FILE_DEF,
                filespec.ECFPLAYER_FIELD_DEF,
                ecfplayerclone,
            )
            applycodesreport.append(
                (
                    fbplayer[constants.BCF_CODE],
                    fbplayer[constants.NAME],
                    "noted as merged into",
                    fbplayer[_MERGECODE_LINE],
                    "in feedback update",
                    repmerge,
                )
            )
            return True

        def update_person(gcode):
            personclone = person.clone()
            personclone.value.playerecfcode = None
            personclone.value.playerecfname = None
            personclone.value.playercode = gcode
            person.edit_record(
                database,
                filespec.MAPECFPLAYER_FILE_DEF,
                filespec.MAPECFPLAYER_FIELD_DEF,
                personclone,
            )
            applycodesreport.append(
                (
                    fbplayer[constants.PIN],
                    fbplayer[constants.NAME],
                    "associated with",
                    gcode,
                )
            )

        def update_player_club():
            try:
                fbplayerpin = int(fbplayer[constants.PIN])
            except ValueError as exc:
                if fbplayer[constants.PIN] != constants.ECF_ZERO_NOT_0:
                    raise ValueError from exc
                fbplayerpin = 0
            player = self._get_ecfmaprecord_for_player(database, fbplayerpin)
            if player:
                playerclone = player.clone()
                playerclone.value.clubecfname = None
                playerclone.value.clubecfcode = None
                playerclone.value.clubcode = fbplayer[constants.CLUB_CODE]
                player.edit_record(
                    database,
                    filespec.MAPECFCLUB_FILE_DEF,
                    filespec.MAPECFCLUB_FIELD_DEF,
                    playerclone,
                )
                applycodesreport.append(
                    (
                        fbplayer[constants.PIN],
                        fbplayer[constants.NAME],
                        "associated with club",
                        fbplayer[constants.CLUB_CODE],
                        fbplayer[constants.CLUB],
                        "on club list",
                    )
                )

        applycodesreport = []
        self.allowapplycodes = False
        database = self.get_appsys().get_results_database()
        database.start_transaction()
        for fbplayer in self.newcodesapply:
            try:
                fbplayerpin = int(fbplayer[constants.PIN])
            except ValueError as exc:
                if fbplayer[constants.PIN] != constants.ECF_ZERO_NOT_0:
                    raise ValueError from exc
                fbplayerpin = 0
            if fbplayer[_PIN_LINE]:
                person = self._get_ecfmaprecord_for_new_person(
                    database, fbplayerpin
                )
                if person:
                    ecfgcode = fbplayer[_NEWCODE_LINE]
                    if fbplayer[_USECODE_LINE]:
                        ecfgcode = fbplayer[_USECODE_LINE]
                    if ecfgcode:
                        if (
                            ecfrecord.get_ecf_player_for_grading_code(
                                database, ecfgcode
                            )
                            is None
                        ):
                            new_ecf_player(ecfgcode)
                        update_person(ecfgcode)
                if self._is_ecf_club_code_a_new_club(
                    database, fbplayer[constants.CLUB_CODE]
                ):
                    new_club()
                update_player_club()
            else:
                ecfplayer = ecfrecord.get_ecf_player_for_grading_code(
                    database, fbplayer[constants.BCF_CODE]
                )
                if ecfplayer is None:
                    # Get pylint E1111 report (assignment-from-no-return)
                    # with no return statement in function.
                    # Get pylint E1128 report (assignment-from-none)
                    # with 'return None' statement in function.
                    callup = new_ecf_player(fbplayer[constants.BCF_CODE])
                else:
                    callup = update_ecf_player()
                person = self._get_ecfmaprecord_for_person(
                    database, fbplayerpin
                )
                if person:
                    if callup:
                        update_person(fbplayer[constants.BCF_CODE])
                if fbplayer[_CLUB_LINE]:
                    if self._is_ecf_club_code_a_new_club(
                        database, fbplayer[constants.CLUB_CODE]
                    ):
                        new_club()
                    update_player_club()
        database.commit()
        self.newcodesapply = []
        self.refresh_controls(
            (
                (
                    database,
                    filespec.MAPECFPLAYER_FILE_DEF,
                    filespec.PERSONMAP_FIELD_DEF,
                ),
                (
                    database,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFPLAYERNAME_FIELD_DEF,
                ),
                (
                    database,
                    filespec.MAPECFCLUB_FILE_DEF,
                    filespec.PLAYERALIASMAP_FIELD_DEF,
                ),
                (
                    database,
                    filespec.ECFCLUB_FILE_DEF,
                    filespec.ECFCLUBNAME_FIELD_DEF,
                ),
                (
                    database,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYERNAME_FIELD_DEF,
                ),
            )
        )
        if applycodesreport:
            self.applyctrl.insert(
                tkinter.END,
                "".join(
                    (
                        "\n\nApply Feedback did following updates:\n\n",
                        "\n".join(["\t".join(e) for e in applycodesreport]),
                    )
                ),
            )
        else:
            self.applyctrl.insert(
                tkinter.END,
                "".join(
                    (
                        "\n\nApply Feedback did no updates.  If some ",
                        "potential updates are reported above it may be ",
                        "because the feedback has already been applied.",
                    )
                ),
            )
        return True

    def describe_buttons(self):
        """Define all action buttons that may appear on Feedback page."""
        super().describe_buttons()
        self.define_button(
            self.btn_closefeedback,
            text="Cancel Apply Feedback",
            tooltip="Cancel the feedback update.",
            underline=0,
            switchpanel=True,
            command=self.on_cancel_apply_feedback,
        )
        self.define_button(
            self._btn_applyfeedback,
            text="Apply Feedback",
            tooltip="Apply feedback updates to database.",
            underline=0,
            command=self.on_apply_feedback,
        )

    def extract_and_report_new_grading_codes(self, lines):
        """Extract new grading codes from feedback and return report."""
        database = self.get_appsys().get_results_database()
        newcodesreport = []
        self.newcodesapply = []
        self.allowapplycodes = False
        ok = True
        pinstart = ": #PIN="
        fieldstart = ": #"
        playerfields = {}

        def report_player(playerfields):
            if _SUBLINE in playerfields:
                if playerfields[_NEWCODE_LINE]:
                    newcodesreport.append(
                        (
                            "New code",
                            playerfields[_NEWCODE_LINE],
                            "for Pin",
                            playerfields[constants.PIN],
                            playerfields[constants.NAME],
                        )
                    )
                if playerfields[_USECODE_LINE]:
                    newcodesreport.append(
                        (
                            "Use code",
                            playerfields[_USECODE_LINE],
                            "for Pin",
                            playerfields[constants.PIN],
                            playerfields[constants.NAME],
                        )
                    )
                if playerfields[_MERGECODE_LINE]:
                    newcodesreport.append(
                        (
                            "    Code",
                            playerfields[constants.BCF_CODE],
                            "    Pin",
                            playerfields[constants.PIN],
                            playerfields[constants.NAME],
                            "",
                            "",
                            "merged with",
                            playerfields[_MERGECODE_LINE],
                        )
                    )
                if playerfields[_PIN_LINE]:
                    if self._is_ecf_club_code_a_new_club(
                        database, playerfields[constants.CLUB_CODE]
                    ):
                        newcodesreport.append(
                            (
                                "        ",
                                "       ",
                                "    Pin",
                                playerfields[constants.PIN],
                                playerfields[constants.NAME],
                                "",
                                "",
                                playerfields[constants.CLUB_CODE],
                                playerfields[constants.CLUB],
                            )
                        )
                elif playerfields[_CLUB_LINE]:
                    if self._is_ecf_club_code_a_new_club(
                        database, playerfields[constants.CLUB_CODE]
                    ):
                        newcodesreport.append(
                            (
                                "        ",
                                playerfields[constants.BCF_CODE],
                                "    Pin",
                                playerfields[constants.PIN],
                                playerfields[constants.NAME],
                                "",
                                "",
                                playerfields[constants.CLUB_CODE],
                                playerfields[constants.CLUB],
                            )
                        )

        database.start_read_only_transaction()
        try:
            for eb in lines:
                e = eb.decode()
                if not e:
                    continue
                if e.startswith(_SUBLINE):
                    report_player(playerfields)
                    if e.find(pinstart) == -1:
                        ok = False
                        break
                    playerfields = {
                        _PIN_LINE: False,
                        _NEWCODE_LINE: False,
                        _USECODE_LINE: False,
                        _MERGECODE_LINE: False,
                        _CLUB_LINE: False,
                    }
                    playerfields[_SUBLINE] = True
                    for fv in e.split(fieldstart, 1)[-1].strip().split("#"):
                        f, v = fv.split("=", 1)
                        playerfields[f] = v
                    self.newcodesapply.append(playerfields)
                elif e.startswith(_PIN_LINE):
                    if e.find(":") == -1:
                        ok = False
                        break
                    start = e.split(":", 1)[0]
                    if not start.endswith(playerfields[constants.PIN]):
                        ok = False
                        break
                    playerfields[_PIN_LINE] = True
                elif e.startswith(_NEWCODE_LINE):
                    playerfields[_NEWCODE_LINE] = e.split()[-1]
                elif e.startswith(_USECODE_LINE):
                    playerfields[_USECODE_LINE] = e.split()[-1]
                elif e.find(_MERGECODE_LINE) > 1:
                    playerfields[_MERGECODE_LINE] = e.split()[-1][:-1]
                elif e.find(_CLUB_LINE) > 1:
                    playerfields[_CLUB_LINE] = True
            else:
                report_player(playerfields)
        finally:
            database.end_read_only_transaction()
        if not newcodesreport:
            return "File has no new player grading codes"
        if ok:
            self.allowapplycodes = True
            return "\n".join(["\t".join(e) for e in newcodesreport])
        return "".join(
            (
                "File may be a feedback file with errors ",
                "in new player sections.\n\n",
                "\n".join(["\t".join(e) for e in newcodesreport]),
            )
        )

    def on_cancel_apply_feedback(self, event=None):
        """Do any tidy up before switching to next panel."""

    def on_apply_feedback(self, event=None):
        """Run apply_new_grading_codes in separate thread."""
        del event
        self.tasklog.run_method(method=self.apply_new_grading_codes)

    def show_buttons_for_cancel_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons((self.btn_closefeedback,))

    def show_buttons_for_start_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (self.btn_closefeedback, self._btn_applyfeedback)
        )

    def _get_ecfmaprecord_for_new_person(self, database, pin):
        """Return ECFmapDBrecordPlayer() for pin or None.

        None is returned if the value attributes make it inappropriate to
        update with a grading code extracted from ECF feedback.  For example
        a grading code has been supplied by editing from the Grading Codes tab.

        """
        rec = resultsrecord.get_alias(database, pin)
        if rec:
            maprec = ecfmaprecord.get_new_person_for_identity(
                database, rec.value
            )
            if maprec:
                if maprec.value.playercode is None:
                    if maprec.value.playerecfcode is None:
                        if maprec.value.playerecfname is not None:
                            return maprec
        return None

    def _get_ecfmaprecord_for_person(self, database, pin):
        """Return ECFmapDBrecordPlayer() for pin or None.

        None is returned if the value attributes make it inappropriate to
        update with a grading code extracted from ECF feedback.  For example
        a grading code has been supplied by editing from the Grading Codes tab.

        """
        rec = resultsrecord.get_alias(database, pin)
        if rec:
            rec = resultsrecord.get_person_from_player(database, rec)
        if rec:
            maprec = ecfmaprecord.get_person_for_alias(
                database, database.encode_record_number(rec.key.pack())
            )
            if maprec:
                if maprec.value.playercode:
                    return maprec
        return None

    def _get_ecfmaprecord_for_player(self, database, pin):
        """Return ECFmapDBrecordClub() for pin or None.

        None is returned if the value attributes make it inappropriate to
        update with a club code extracted from ECF feedback.

        """
        rec = resultsrecord.get_alias(database, pin)
        if rec:
            maprec = ecfmaprecord.get_player_for_alias(
                database, rec.key.pack()
            )
            if maprec:
                if maprec.value.clubcode is None:
                    return maprec
        return None

    def _is_ecf_club_code_a_new_club(self, database, ecfcode):
        """Return True if ecfcode is not on database or False.

        True is returned if the ECF club code does not exist on the reference
        file usually updated from ECF master files.  Assumption is the ecfcode
        is a new club introduced on the submission file for this feedback file.

        False is return if ecfcode is False which means a club code was not
        included in the submission file.

        """
        if ecfcode:
            return not ecfrecord.get_ecf_club_for_club_code(database, ecfcode)
        return False
