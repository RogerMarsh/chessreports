# ogdgradingcodes.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Panel for allocating ECF online grading codes to players."""

from ast import literal_eval
import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel

from . import ogdplayergrids
from ...core.ogd import ecfogdrecord
from ...core.ogd import ecfgcodemaprecord
from ...core import resultsrecord
from ...core import filespec


class ECFGradingCodes(panel.PanedPanelGridSelectorBar):
    """The ECFGradingCodes panel for a Results database."""

    _btn_identify = "ecfgradingcodes_identify"
    _btn_remove_code = "ecfgradingcodes_remove"

    # pylint W0102 dangerous-default-value.
    # cnf used as tkinter.Frame argument, which defaults to {}.
    def __init__(self, parent=None, cnf={}, **kargs):
        """Extend and define the results database ECF grading code panel."""
        self.persongrid = None
        self.ecfpersongrid = None

        super().__init__(parent=parent, cnf=cnf, **kargs)

        self.show_panel_buttons(
            (
                self._btn_identify,
                self._btn_remove_code,
            )
        )
        self.create_buttons()

        # pylint W0632 unbalanced-tuple-unpacking.
        # self.make_grids returns a list with same length as argument.
        self.persongrid, self.ecfpersongrid = self.make_grids(
            (
                {
                    "grid": ogdplayergrids.OGDPersonGrid,
                    "selectlabel": "Select Player:  ",
                    "gridfocuskey": "<KeyPress-F7>",
                    "selectfocuskey": "<KeyPress-F5>",
                },
                {
                    "grid": ogdplayergrids.ECFOGDPersonGrid,
                    "selectlabel": "Select Player Reference:  ",
                    "gridfocuskey": "<KeyPress-F8>",
                    "selectfocuskey": "<KeyPress-F6>",
                },
            )
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container
        """

    def describe_buttons(self):
        """Define all action buttons for ECF grading code page."""
        super().describe_buttons()
        self.define_button(
            self._btn_identify,
            text="Link Grading Code",
            tooltip="Link selected player with selected Grading Code.",
            underline=1,
            command=self.on_identify,
        )
        self.define_button(
            self._btn_remove_code,
            text="Break Grading Code link",
            tooltip="Break link between player and ECF grading code.",
            underline=0,
            command=self.on_remove_code,
        )

    def on_identify(self, event=None):
        """Link a player name with a grading code record."""
        del event
        self.select_grading_code()
        self.ecfpersongrid.set_select_hint_label()
        return "break"

    def on_remove_code(self, event=None):
        """Dialogue to break player name link to grading code record."""
        del event
        self.remove_grading_code()
        return "break"

    def remove_grading_code(self):
        """Break link between player name and grading code record."""
        msgtitle = "Grading Codes"
        psel = self.persongrid.selection
        if len(psel) == 0:
            msg = " ".join(
                (
                    "Select the player whose ECF grading code",
                    "link will be removed.",
                )
            )
            tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        mr = ecfgcodemaprecord.get_person_for_player(db, psel[0][-1])
        if mr is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db,
                            self.persongrid.objects[psel[0]].value.identity(),
                        ),
                        "\nis not linked to a grading code.",
                    )
                ),
                title=msgtitle,
            )
            return

        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Confirm Grading Code ",
                    mr.value.playercode,
                    " to be removed from\n",
                    resultsrecord.get_player_name_text(
                        db, self.persongrid.objects[psel[0]].value.identity()
                    ),
                    ".",
                )
            ),
            title=msgtitle,
        ):
            return

        db.start_transaction()
        mr.delete_record(db, filespec.MAPECFOGDPLAYER_FILE_DEF)
        db.commit()
        if psel[0] in self.persongrid.bookmarks:
            self.persongrid.bookmarks.remove(psel[0])
        self.persongrid.selection[:] = []
        self.refresh_controls((self.persongrid,))
        return

    def select_grading_code(self):
        """Link player to ECF grading code after confirmation dialogue."""
        msgtitle = "Grading Codes"
        psel = self.persongrid.selection
        epsel = self.ecfpersongrid.selection
        if len(psel) + len(epsel) != 2:
            if len(psel) + len(epsel) == 0:
                msg = "Select a player and an ECF grading code."
            elif len(psel) == 0:
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
        selrec = self.persongrid.objects[psel[0]]
        linkrec = ecfgcodemaprecord.get_person_for_player(db, psel[0][-1])
        if linkrec:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db, selrec.value.identity()
                        ),
                        "\nis linked to grading code ",
                        linkrec.value.playercode,
                        ".\nIf the new link is correct you will need to ",
                        "break the existing link first and then assign the ",
                        "new grading code for this player.",
                    )
                ),
                title=msgtitle,
            )
            return
        ecfrec = ecfogdrecord.get_ecf_ogd_player(db, epsel[0][-1])
        cpc = ecfgcodemaprecord.get_person_for_grading_code(
            db, ecfrec.value.ECFOGDcode
        )
        if cpc is not None:
            aliasrec = resultsrecord.get_alias(
                db, literal_eval(cpc.value.playerkey)
            )
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Grading Code ",
                        ecfrec.value.ECFOGDcode,
                        " is already linked to\n",
                        resultsrecord.get_player_name_text(
                            db, aliasrec.value.identity()
                        ),
                        ".\nIf the new link is correct you will need to ",
                        "break the existing link first and assign grading ",
                        "codes for both players as appropriate.",
                    )
                ),
                title=msgtitle,
            )
            return

        if selrec.value.merge is False:
            pselkey = selrec.key.recno
        elif selrec.value.merge is True:
            pselkey = None
        elif selrec.value.merge is None:
            pselkey = None
        else:
            aliasrec = resultsrecord.get_alias(db, selrec.value.merge)
            if selrec.value.merge is False:
                pselkey = aliasrec.key.recno
            else:
                pselkey = None
        if pselkey is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db, selrec.value.identity()
                        ),
                        "\n is not an identified player",
                        ".\nCannot proceed with grading code allocation",
                        " until the existing link is removed.",
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
                    ecfrec.value.ECFOGDcode,
                    self.ecfpersongrid.objects[epsel[0]].value.ECFOGDname.join(
                        (" (", ")")
                    ),
                    "\nto be linked to\n",
                    resultsrecord.get_player_name_text(
                        db,
                        resultsrecord.get_unpacked_player_identity(
                            self.persongrid.objects[
                                psel[0]
                            ].value.identity_packed()
                        ),
                    ),
                    ".",
                )
            ),
            title=msgtitle,
        ):
            return

        selrec = self.persongrid.objects[psel[0]]
        newmr = ecfgcodemaprecord.ECFmapOGDrecordPlayer()
        newmr.key.recno = None
        newmr.value.playercode = ecfrec.value.ECFOGDcode
        newmr.value.playerkey = repr(pselkey)
        db.start_transaction()
        newmr.put_record(db, filespec.MAPECFOGDPLAYER_FILE_DEF)
        db.commit()
        if psel[0] in self.persongrid.bookmarks:
            self.persongrid.bookmarks.remove(psel[0])
        if epsel[0] in self.ecfpersongrid.bookmarks:
            self.ecfpersongrid.bookmarks.remove(epsel[0])
        self.ecfpersongrid.selection[:] = []
        self.persongrid.selection[:] = []
        self.clear_selector(True)
        self.ecfpersongrid.set_grid_properties()
        self.refresh_controls((self.persongrid, self.ecfpersongrid))
        return
