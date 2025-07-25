# ecfgradingcodes.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database panel for allocating ECF grading codes."""

import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel

from ...core.ecf import ecfrecord
from ...core.ecf import ecfmaprecord
from ...core import resultsrecord
from ...core import filespec
from . import ecfplayergrids
from . import ecfdetail


class ECFGradingCodes(panel.PanedPanelGridSelectorBar):
    """The ECFGradingCodes panel for a Results database."""

    _btn_identify = "ecfgradingcodes_identify"
    _btn_revert = "ecfgradingcodes_revert"
    _btn_ecf_name = "ecfgradingcodes_name"
    _btn_grading_code = "ecfgradingcodes_grading_code"
    _btn_grading_code_download = "ecfgradingcodes_grading_code_download"
    _btn_ecf_name_download = "ecfgradingcodes_ecf_name_download"
    _btn_cancel_edit_ecf_name = "ecfgradingcodes_cancel"

    # pylint W0102 dangerous-default-value.
    # cnf used as tkinter.Frame argument, which defaults to {}.
    def __init__(self, parent=None, cnf={}, **kargs):
        """Extend and define the results database ECF grading code panel."""
        self.newpersongrid = None
        self.ecfpersongrid = None

        super().__init__(parent=parent, cnf=cnf, **kargs)

        self.show_panel_buttons(
            (
                self._btn_identify,
                self._btn_revert,
                self._btn_ecf_name,
                self._btn_grading_code,
                self._btn_cancel_edit_ecf_name,
                self._btn_grading_code_download,
            )
        )
        self.create_buttons()

        # pylint W0632 unbalanced-tuple-unpacking.
        # self.make_grids returns a list with same length as argument.
        self.newpersongrid, self.ecfpersongrid = self.make_grids(
            (
                {
                    "grid": ecfplayergrids.NewPersonGrid,
                    "selectlabel": "Select New Player:  ",
                    "gridfocuskey": "<KeyPress-F7>",
                    "selectfocuskey": "<KeyPress-F5>",
                },
                {
                    "grid": ecfplayergrids.ECFPersonGrid,
                    "selectlabel": "Select Player Reference:  ",
                    "gridfocuskey": "<KeyPress-F8>",
                    "selectfocuskey": "<KeyPress-F6>",
                },
            )
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """

    def describe_buttons(self):
        """Define action buttons that may appear on ECF grading code page."""
        super().describe_buttons()
        self.define_button(
            self._btn_identify,
            text="Link ECF Code",
            tooltip="Link selected player with selected ECF Code.",
            underline=1,
            command=self.on_identify,
        )
        self.define_button(
            self._btn_revert,
            text="Adjust Identity",
            tooltip="".join(
                (
                    "Remove player from Rating Codes tab ",
                    "(to adjust identification).",
                )
            ),
            underline=2,
            command=self.on_revert,
        )
        self.define_button(
            self._btn_ecf_name,
            text="New ECF Name",
            tooltip="Edit new player name for ECF submission file.",
            underline=10,
            command=self.on_ecf_name,
        )
        self.define_button(
            self._btn_grading_code,
            text="New ECF Code",
            tooltip="Edit new player ECF code for ECF submission file.",
            underline=9,
            command=self.on_grading_code,
        )
        self.define_button(
            self._btn_cancel_edit_ecf_name,
            text="Cancel Edit ECF Name",
            tooltip="Cancel edit player name from master file.",
            underline=10,
            command=self.on_cancel_edit_ecf_name,
        )
        self.define_button(
            self._btn_ecf_name_download,
            text="Download ECF Name",
            tooltip="Download player's name from ECF.",
            underline=4,
            command=self.on_ecf_name_download,
        )
        self.define_button(
            self._btn_grading_code_download,
            text="Download ECF Code",
            tooltip="Download player's details from ECF.",
            underline=2,
            command=self.on_grading_code_download,
        )

    def cancel_edit_player_ecf_name(self):
        """Remove player from new player grid cancelling ECF name edit."""
        msgtitle = "Player Name"
        npsel = self.newpersongrid.selection
        if len(npsel) == 0:
            msg = " ".join(
                (
                    "Select the player whose ECF form of name",
                    "edit is to be cancelled.",
                )
            )
            tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        db.start_read_only_transaction()
        try:
            mr = ecfmaprecord.get_person(db, npsel[0][-1])
            if mr is None:
                pr = ecfmaprecord.ECFmapDBrecordPlayer()
                pr.load_record(self.newpersongrid.objects[npsel[0]])
                name_text = resultsrecord.get_player_name_text(
                    db, pr.value.get_unpacked_playername()
                )
            elif mr.value.playercode is None:
                name_text = resultsrecord.get_player_name_text(
                    db, mr.value.get_unpacked_playername()
                )
            else:
                name_text = resultsrecord.get_player_name_text(
                    db, mr.value.get_unpacked_playername()
                )
        finally:
            db.end_read_only_transaction()
        if mr is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord has been deleted.\nCannot ",
                        "proceed with amendment of ECF version of name.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr.value.playercode is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord is not linked to an ECF grading code ",
                        "record so Cancel Edit is not allowed.\nUse Identify ",
                        "to link the player to an ECF grading code or Edit ",
                        "Name and Grading code to specify the details ",
                        "for a new player.",
                    )
                ),
                title=msgtitle,
            )
            return

        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Confirm edit of ECF version of name of\n",
                    name_text,
                    "\nto be cancelled.",
                )
            ),
            title=msgtitle,
        ):
            return

        newmr = mr.clone()
        newmr.value.playerecfcode = None
        newmr.value.playerecfname = None
        db.start_transaction()
        mr.edit_record(
            db,
            filespec.MAPECFPLAYER_FILE_DEF,
            filespec.MAPECFPLAYER_FIELD_DEF,
            newmr,
        )
        db.commit()
        if npsel[0] in self.newpersongrid.bookmarks:
            self.newpersongrid.bookmarks.remove(npsel[0])
        self.newpersongrid.selection[:] = []
        self.refresh_controls((self.newpersongrid,))
        return

    def edit_new_player_ecf_name(self):
        """Show edit dialogue for ECF form of new player's name."""
        msgtitle = "New Player Name"
        npsel = self.newpersongrid.selection
        if len(npsel) == 0:
            msg = " ".join(
                (
                    "Select the new player whose ECF form of name",
                    "is to be modified (probably before first",
                    "submission of results for the new player).",
                )
            )
            tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        db.start_read_only_transaction()
        try:
            mr = ecfmaprecord.get_person(db, npsel[0][-1])
            if mr is None:
                pr = ecfmaprecord.ECFmapDBrecordPlayer()
                pr.load_record(self.newpersongrid.objects[npsel[0]])
                name_text = resultsrecord.get_player_name_text(
                    db, pr.value.get_unpacked_playername()
                )
            else:
                name_text = resultsrecord.get_player_name_text(
                    db, mr.value.get_unpacked_playername()
                )
        finally:
            db.end_read_only_transaction()
        if mr is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord has been deleted.\nCannot ",
                        "proceed with amendment of ECF version of name.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr.value.playerecfcode:
            if mr.value.playercode is None:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            name_text,
                            "\nrecord has ECF Grading Code.\nCannot ",
                            "proceed with amendment of ECF version of name.",
                        )
                    ),
                    title=msgtitle,
                )
                return

        mr.database = db
        # Is it a design flaw having to set mr.dbname this way? And what to do?
        mr.dbname = self.newpersongrid.datasource.dbset
        dlg = ecfdetail.ECFNameDialog(None, mr)
        if dlg.is_yes():
            self.refresh_controls((self.newpersongrid,))

    def edit_new_player_grading_code(self):
        """Show dialogue to edit player's ECF grading code and do update."""
        msgtitle = "New Player Grading Code"
        if tkinter.messagebox.askokcancel(
            parent=self.get_widget(),
            message=" ".join(
                (
                    "This action became obsolete when the ECF introduced the",
                    "programming API to monthly rating.\n\nPrefer the",
                    "'Download ECF Code' followed by 'Link ECF Code' actions",
                    "instead.\n\nSelect OK to accept the recommendation.",
                )
            ),
            title=msgtitle,
        ):
            return
        npsel = self.newpersongrid.selection
        if len(npsel) == 0:
            msg = " ".join(
                (
                    "Select the new player whose ECF grading code is",
                    "to be modified (probably following receipt",
                    "of feedback file from ECF).",
                )
            )
            tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        db.start_read_only_transaction()
        try:
            mr = ecfmaprecord.get_person(db, npsel[0][-1])
            if mr is None:
                pr = ecfmaprecord.ECFmapDBrecordPlayer()
                pr.load_record(self.newpersongrid.objects[npsel[0]])
                name_text = resultsrecord.get_player_name_text(
                    db, pr.value.get_unpacked_playername()
                )
            else:
                name_text = resultsrecord.get_player_name_text(
                    db, mr.value.get_unpacked_playername()
                )
        finally:
            db.end_read_only_transaction()
        if mr is None:
            pr = ecfmaprecord.ECFmapDBrecordPlayer()
            pr.load_record(self.newpersongrid.objects[npsel[0]])
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord has been deleted.\nCannot ",
                        "proceed with amendment of grading code.",
                    )
                ),
                title=msgtitle,
            )
            return
        if not mr.value.playerecfname:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord has no ECF version of name.\nCannot ",
                        "proceed with amendment of grading code.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr.value.playercode:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord is linked to an ECF grading code record ",
                        mr.value.playercode,
                        " so editing the grading code is not allowed.\n",
                        "Use ECF Name to edit the name or Cancel Edit ",
                        "to remove player from this grid.",
                    )
                ),
                title=msgtitle,
            )
            return

        mr.database = db
        # Is it a design flaw having to set mr.dbname this way? And what to do?
        mr.dbname = self.newpersongrid.datasource.dbset
        dlg = ecfdetail.ECFGradingCodeDialog(None, mr)
        if dlg.is_yes():
            self.refresh_controls((self.newpersongrid,))

    def download_new_player_grading_code(self):
        """Show dialogue to download player's ECF code and do update."""
        db = self.get_appsys().get_results_database()

        dlg = ecfdetail.ECFDownloadGradingCodeDialog(None, db)
        if dlg.is_yes():
            self.refresh_controls((self.ecfpersongrid,))

    def download_ecf_name_for_ecf_code(self):
        """Show dialogue to download player's ECF name and do update."""
        db = self.get_appsys().get_results_database()

        dlg = ecfdetail.ECFDownloadPlayerNameDialog(None, db)
        if dlg.is_yes():
            self.refresh_controls((self.ecfpersongrid,))

    def on_identify(self, event=None):
        """Link a player name with a grading code record."""
        del event
        self.select_grading_code()
        self.ecfpersongrid.set_select_hint_label()
        return "break"

    def on_revert(self, event=None):
        """Break link between player name and grading code record."""
        del event
        self.return_person_for_identification()
        return "break"

    def on_ecf_name(self, event=None):
        """Edit the locally entered player name in ECF name format."""
        del event
        self.edit_new_player_ecf_name()
        return "break"

    def on_cancel_edit_ecf_name(self, event=None):
        """Cancel editing of locally entered player name in ECF name format."""
        del event
        self.cancel_edit_player_ecf_name()
        return "break"

    def on_grading_code(self, event=None):
        """Edit the locally entered ECF code."""
        del event
        self.edit_new_player_grading_code()
        return "break"

    def on_grading_code_download(self, event=None):
        """Download the locally entered ECF code."""
        del event
        self.download_new_player_grading_code()
        return "break"

    def on_ecf_name_download(self, event=None):
        """Download the ECF name for the locally entered ECF code."""
        del event
        self.download_ecf_name_for_ecf_code()
        return "break"

    def return_person_for_identification(self):
        """Remove player from grading code page after confirmation dialogue.

        Only needs to be done if player is to be merged into another player.
        Players merged into this player can be remerged without doing this.

        """
        msgtitle = "Grading Codes"
        npsel = self.newpersongrid.selection
        if len(npsel) == 0:
            msg = " ".join(
                (
                    "Select the player to be removed from this tab",
                    "for adjustment of identification.",
                )
            )
            tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        db.start_read_only_transaction()
        try:
            mr = ecfmaprecord.get_person(db, npsel[0][-1])
            if mr is None:
                pr = ecfmaprecord.ECFmapDBrecordPlayer()
                pr.load_record(self.newpersongrid.objects[npsel[0]])
                name_text = resultsrecord.get_player_name_text(
                    db, pr.value.get_unpacked_playername()
                )
            else:
                name_text = resultsrecord.get_player_name_text(
                    db, mr.value.get_unpacked_playername()
                )
        finally:
            db.end_read_only_transaction()
        if mr is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord has been deleted.\nCannot ",
                        "proceed with adjustment of identification.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr.value.playercode:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord is linked to an ECF grading code record ",
                        mr.value.playercode,
                        " so releasing player for adjustment on Player tabs ",
                        "is not allowed.\n",
                        "Use ECF Name to edit the name or Cancel Edit ",
                        "to remove player from this grid.",
                    )
                ),
                title=msgtitle,
            )
            return
        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Confirm\n",
                    name_text,
                    "\nto be removed from this tab ",
                    "for adjustment of identification.",
                )
            ),
            title=msgtitle,
        ):
            return

        db.start_transaction()
        mr.delete_record(db, filespec.MAPECFPLAYER_FILE_DEF)
        db.commit()
        if npsel[0] in self.newpersongrid.bookmarks:
            self.newpersongrid.bookmarks.remove(npsel[0])
        self.newpersongrid.selection[:] = []
        self.refresh_controls((self.newpersongrid,))
        return

    def select_grading_code(self):
        """Link player to ECF grading code after confirmation dialogue."""
        msgtitle = "Grading Codes"
        npsel = self.newpersongrid.selection
        epsel = self.ecfpersongrid.selection
        if len(npsel) + len(epsel) != 2:
            if len(npsel) + len(epsel) == 0:
                msg = "Select a player and an ECF grading code."
            elif len(npsel) == 0:
                msg = " ".join(
                    (
                        "Select the player to be linked to",
                        "the selected ECF grading code.",
                    )
                )
            else:
                msg = " ".join(
                    (
                        "Select the ECF grading code to be linked to",
                        "the selected player.",
                    )
                )

            tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        db.start_read_only_transaction()
        try:
            ecfrec = ecfrecord.get_ecf_player(db, epsel[0][-1])
            cpc = ecfmaprecord.get_person_for_grading_code(
                db, ecfrec.value.ECFcode
            )
            if cpc is None:
                mr = ecfmaprecord.get_person(db, npsel[0][-1])
                if mr is None:
                    pr = ecfmaprecord.ECFmapDBrecordPlayer()
                    pr.load_record(self.newpersongrid.objects[npsel[0]])
                    name_text = resultsrecord.get_player_name_text(
                        db, pr.value.get_unpacked_playername()
                    )
                elif mr.value.playercode:
                    name_text = resultsrecord.get_player_name_text(
                        db, mr.value.get_unpacked_playername()
                    )
                else:
                    name_text = resultsrecord.get_player_name_text(
                        db,
                        resultsrecord.get_unpacked_player_identity(
                            self.newpersongrid.objects[
                                npsel[0]
                            ].value.playername
                        ),
                    )
            else:
                name_text = resultsrecord.get_player_name_text(
                    db, cpc.value.get_unpacked_playername()
                )
        finally:
            db.end_read_only_transaction()
        if cpc is not None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Grading Code ",
                        ecfrec.value.ECFcode,
                        " is already linked to\n",
                        name_text,
                        ".\nIf the new link is correct you will need either ",
                        "to return the new player to the New Player tab and ",
                        "merge with the player who has the grading code ",
                        "(correctly) or to break the existing link and ",
                        "assign grading codes for both players.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord has been deleted.\n",
                        "Cannot proceed with grading code allocation.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr.value.playercode:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        name_text,
                        "\nrecord is linked to an ECF grading code record ",
                        mr.value.playercode,
                        " so linking player to another grading code is ",
                        "not allowed.\n",
                        "Use ECF Name to edit the name or Cancel Edit ",
                        "to remove player from this grid.",
                    )
                ),
                title=msgtitle,
            )
            return

        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Confirm Grading Code\n",
                    ecfrec.value.ECFcode,
                    self.ecfpersongrid.objects[epsel[0]].value.ECFname.join(
                        (" (", ")")
                    ),
                    "\nto be linked to\n",
                    name_text,
                    ".",
                )
            ),
            title=msgtitle,
        ):
            return

        newmr = mr.clone()
        newmr.value.playercode = ecfrec.value.ECFcode
        newmr.value.playerecfcode = None
        newmr.value.playerecfname = None
        db.start_transaction()
        mr.edit_record(
            db,
            filespec.MAPECFPLAYER_FILE_DEF,
            filespec.MAPECFPLAYER_FIELD_DEF,
            newmr,
        )
        db.commit()
        if npsel[0] in self.newpersongrid.bookmarks:
            self.newpersongrid.bookmarks.remove(npsel[0])
        if epsel[0] in self.ecfpersongrid.bookmarks:
            self.ecfpersongrid.bookmarks.remove(epsel[0])
        self.ecfpersongrid.selection[:] = []
        self.newpersongrid.selection[:] = []
        self.clear_selector(True)
        self.ecfpersongrid.set_grid_properties()
        self.refresh_controls(
            (
                self.newpersongrid,
                (db, filespec.PLAYER_FILE_DEF, filespec.PLAYERNAME_FIELD_DEF),
            )
        )
        return
