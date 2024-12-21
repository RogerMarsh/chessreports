# prepareresults.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Prepare ECF submission files and League database dumps for Results input.

This module allows event data held on a League database to be prepared for
input into a Berkeley DB or DPT results database.  The ECF submission file
format is used to transfer the data because it is the only output generated
by any grading program in a known and fit for purpose format.

The assumption necessary is that a PIN value refers to the same LPLAYER
across submission files.

A restriction is that use of a PIN that looks like an ECF grading code is
sufficient to prevent this module making the assumption for the LPLAYER.
(The League program does not use the grading code as PIN.)

BCF CODE; CLUB NAME; CLUB (non-standard for CLUB NAME); CLUB CODE;
and CLUB COUNTY fields on submission files are removed.

(There is a data dump program for League databases and that format is
supported here. The data dump program is available to graders on request.
The only advantage from using this program is that all the data is in
a single file making it difficult to forget some data.)

"""

import os
import collections

from . import constants as cc


class PrepareResults:
    """Class for importing results data."""

    def __init__(self, container):
        """Initialise data structures for import from files in container."""
        super().__init__()
        self.container = container
        self.pinprefix = os.path.splitext(os.path.basename(container))[0]
        self.files = set()
        self.keeppinvaluemap = {}
        self.filenewtextmap = {}
        self.error = []

    def empty_extract(self):
        """Return False."""
        return False

    def _translate_results_format(
        self,
        context=None,
        keymap=None,
        validmap=None,
        pinreadmap=None,
        pinmap=None,
        gradingcodemap=None,
        discardmap=None,
        copy_lines=True,
    ):
        """Extract results into a common format.

        Provide rules in context and keymap arguments.

        """

        def null(lines, text):
            """Do nothing."""  # Avoid pylint W0613 if 'pass' instead.
            del lines, text

        def null_extend(lines, text, data):
            """Do nothing."""  # Avoid pylint W0613 if 'pass' instead.
            del lines, text, data

        def copy_text(lines, text):
            lines.append(text)

        def copy_text_extend(lines, text, data):
            del data
            lines.extend(text)

        if copy_lines:
            process = copy_text
        else:
            process = null

        if context is None:
            context = {}
        for c in context:
            if not isinstance(context[c], collections.abc.Callable):
                if context[c] is True:
                    context[c] = copy_text_extend
                else:
                    context[c] = null_extend
        if keymap is None:
            keymap = {}
        if validmap is None:
            validmap = {}
        if pinreadmap is None:
            pinreadmap = set()
        if pinmap is None:
            pinmap = set()
        if gradingcodemap is None:
            gradingcodemap = set()
        if discardmap is None:
            discardmap = set()

        pinvaluemap = {}
        keeppins = pinreadmap - pinmap
        cc_gccc = cc.GRADING_CODE_CHECK_CHARACTERS  # avoid long line later
        extract = []
        filesprocessed = [None]
        for f, text in self.get_lines():
            fault = False
            filesprocessed.append(f)
            lines = []
            record = []
            data = {}
            for t in text:
                ts = t.split("=", 1)
                key, value = ts[0], ts[-1]
                if key not in validmap:
                    if len(key) != 0:
                        self.error.append(
                            (
                                filesprocessed[-2:],
                                ("Keyword not expected : ", key),
                            )
                        )
                        fault = True
                        break
                else:
                    vm = validmap[key]
                    if isinstance(vm, str):
                        if contextkey != vm:
                            self.error.append(
                                (
                                    filesprocessed[-2:],
                                    (
                                        "Keyword ",
                                        key,
                                        " not expected after keyword ",
                                        contextkey,
                                    ),
                                )
                            )
                            fault = True
                            break
                    elif isinstance(vm, dict):
                        if contextkey not in vm:
                            self.error.append(
                                (
                                    filesprocessed[-2:],
                                    (
                                        "Keyword ",
                                        key,
                                        " not expected after keyword ",
                                        contextkey,
                                    ),
                                )
                            )
                            fault = True
                            break
                    elif vm is not None:
                        self.error.append(
                            (
                                filesprocessed[-2:],
                                (
                                    "Unable to determine validity of keyword ",
                                    key,
                                ),
                            )
                        )
                        fault = True
                        break
                if key in context:
                    if record:
                        context[contextkey](lines, record, data)
                    contextkey = key
                    data.clear()
                    record = []
                # keymap values may make the discard map superfluous
                # GCODE is in keymap but BCF_CODE is not and so on
                if key in keymap:
                    if key in pinmap:
                        if value not in pinvaluemap:
                            if len(value) != cc.GRADING_CODE_LENGTH:
                                pinvaluemap[value] = value
                            elif value[-1] in cc_gccc and value[:-1].isdigit():
                                pinvaluemap[value] = "-".join(
                                    (self.pinprefix, str(len(pinvaluemap)))
                                )
                            else:
                                pinvaluemap[value] = value
                    if key in pinreadmap:
                        try:
                            process(
                                record, "=".join((key, pinvaluemap[value]))
                            )
                        except KeyError:
                            self.error.append(
                                (
                                    filesprocessed[-2:],
                                    (
                                        "PIN ",
                                        value,
                                        " for field ",
                                        key,
                                        " is not in PIN map",
                                    ),
                                )
                            )
                            fault = True
                            break
                        data[keymap[key]] = pinvaluemap[value]
                        if key in keeppins:
                            if value not in self.keeppinvaluemap:
                                self.keeppinvaluemap[value] = pinvaluemap[
                                    value
                                ]
                    elif key not in discardmap:
                        process(record, t)
                        data[keymap[key]] = value
                elif key in gradingcodemap:
                    if cc.LPCODE in data:
                        if len(value) == cc.GRADING_CODE_LENGTH:
                            if value[:-1] in data[cc.LPCODE]:
                                self.error.append(
                                    (
                                        filesprocessed[-2:],
                                        (
                                            "Grading code ",
                                            value,
                                            " is included in LPLAYER pin ",
                                            data[cc.LPCODE],
                                        ),
                                    )
                                )
                                fault = True
                                break
                elif key in context:
                    process(record, t)
            if fault:
                continue
            if record:
                context[contextkey](lines, record, data)
            extract.append((f, lines))

        return extract

    def get_folder_contents(self, container):
        """Add file names in directory container to self.list."""
        for f in os.listdir(container):
            fn = os.path.join(container, f)
            if os.path.isfile(fn):
                self.files.add(fn)
            elif os.path.isdir(fn):
                self.get_folder_contents(fn)

    def get_lines(self):
        """Return lines of text from file.

        Extend get_lines method in subclass if self.textlines needs
        transforming before being processed by translate_results_format method.

        """
        self.get_folder_contents(self.container)
        filetext = []
        for f in self.files:
            with open(f, "r", encoding="utf8") as ofile:  # 'rb'?
                filetext.append((f, [t.rstrip() for t in ofile.readlines()]))
        return filetext

    def extract_data_from_import_files(self, importfiles=None):
        """Return list containing processed import file contents."""
        if importfiles is None:
            importfiles = [("No files to display", [])]
        # Subclasses provide the report_file method.
        # pylint: disable-next=no-member.
        return [self.report_file(f, t) for f, t in importfiles]


class PrepareSubmissionFile(PrepareResults):
    """Import data from file formatted as ECF results submission file."""

    def translate_results_format(self):
        """Translate results to internal format."""
        # context copied from merges.py and value part of key:value
        # changed as necessary
        context = {
            cc.EVENT_DETAILS: True,
            cc.PLAYER_LIST: True,
            cc.OTHER_RESULTS: True,
            cc.MATCH_RESULTS: True,
            cc.SECTION_RESULTS: True,
            cc.FINISH: True,
            cc.PIN: True,
            cc.PIN1: True,
        }

        # keymap copied from merges.py unchanged but it could be a set here
        keymap = {
            cc.EVENT_CODE: cc.LECODE,
            cc.EVENT_NAME: cc.LENAME,
            cc.EVENT_DATE: cc.LEDATE,
            cc.FINAL_RESULT_DATE: cc.LEFINALDATE,
            cc.PIN: cc.LPCODE,
            cc.NAME: cc.LPNAME,
            cc.OTHER_RESULTS: cc.LMNAME,
            cc.MATCH_RESULTS: cc.LMNAME,
            cc.SECTION_RESULTS: cc.LMNAME,
            cc.RESULTS_DATE: cc.LMDATE,
            cc.PIN1: cc.LPCODE1,
            cc.PIN2: cc.LPCODE2,
            cc.ROUND: cc.LGROUND,
            cc.BOARD: cc.LGBOARD,
            cc.COLOUR: cc.LGCOLOR,
            cc.SCORE: cc.LGRESULT,
            cc.GAME_DATE: cc.LGDATE,
            cc.WHITE_ON: cc.LMCOLOR,
            # cc.CLUB:cc.LCNAME, #League program for CLUB NAME
            # cc.CLUB_NAME:cc.LCNAME,
            cc.SURNAME: cc.E_SURNAME,
            cc.INITIALS: cc.E_INITIALS,
            cc.FORENAME: cc.E_FORENAME,
        }

        # validmap copied from merges.py unchanged but it could be a set here
        # validmap accepts a few field sequences that are not accepted by the
        # ECF Checker program to simplify spotting field group boundaries and
        # presence of invalid fields.
        # COLUMN; TABLE END; and TABLE START expanded in get_lines so removed
        # from validmap. Appearance in return value indicates a table format
        # error.
        validmap = {
            cc.ADJUDICATED: cc.EVENT_DETAILS,
            cc.BCF_CODE: cc.PIN,
            cc.BCF_NO: cc.PIN,
            cc.BOARD: {
                cc.MATCH_RESULTS: None,
                cc.PIN1: None,
            },
            cc.CLUB: cc.PIN,  # League program for CLUB NAME
            cc.CLUB_CODE: cc.PIN,
            cc.CLUB_COUNTY: cc.PIN,
            cc.CLUB_NAME: cc.PIN,
            cc.COLOUR: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
            },
            cc.COMMENT: {
                cc.PIN: None,
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
            },
            cc.DATE_OF_BIRTH: cc.PIN,
            cc.EVENT_CODE: cc.EVENT_DETAILS,
            cc.EVENT_DATE: cc.EVENT_DETAILS,
            cc.EVENT_DETAILS: None,
            cc.EVENT_NAME: cc.EVENT_DETAILS,
            cc.FIDE_NO: cc.PIN,
            cc.FINAL_RESULT_DATE: cc.EVENT_DETAILS,
            cc.FINISH: None,
            cc.FORENAME: cc.PIN,
            cc.GAME_DATE: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
            },
            cc.GENDER: cc.PIN,
            cc.INFORM_CHESSMOVES: cc.EVENT_DETAILS,
            cc.INFORM_FIDE: cc.EVENT_DETAILS,
            cc.INFORM_GRAND_PRIX: cc.EVENT_DETAILS,
            cc.INFORM_UNION: cc.EVENT_DETAILS,
            cc.INITIALS: cc.PIN,
            cc.MATCH_RESULTS: None,
            cc.MINUTES_FIRST_SESSION: cc.EVENT_DETAILS,
            cc.MINUTES_FOR_GAME: cc.EVENT_DETAILS,
            cc.MINUTES_REST_OF_GAME: cc.EVENT_DETAILS,
            cc.MINUTES_SECOND_SESSION: cc.EVENT_DETAILS,
            cc.MOVES_FIRST_SESSION: cc.EVENT_DETAILS,
            cc.MOVES_SECOND_SESSION: cc.EVENT_DETAILS,
            cc.NAME: cc.PIN,
            cc.OTHER_RESULTS: None,
            cc.PIN: {
                cc.PLAYER_LIST: None,
                cc.PIN: None,
            },
            cc.PIN1: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
            },
            cc.PIN2: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
            },
            cc.PLAYER_LIST: None,
            cc.RESULTS_DATE: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
            },
            cc.RESULTS_DUPLICATED: cc.EVENT_DETAILS,
            cc.RESULTS_OFFICER: cc.EVENT_DETAILS,
            cc.RESULTS_OFFICER_ADDRESS: cc.EVENT_DETAILS,
            cc.ROUND: {
                cc.SECTION_RESULTS: None,
                cc.PIN1: None,
            },
            cc.SCORE: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
            },
            cc.SECONDS_PER_MOVE: cc.EVENT_DETAILS,
            cc.SECTION_RESULTS: None,
            cc.SUBMISSION_INDEX: cc.EVENT_DETAILS,
            cc.SURNAME: cc.PIN,
            cc.TITLE: cc.PIN,
            cc.TREASURER: cc.EVENT_DETAILS,
            cc.TREASURER_ADDRESS: cc.EVENT_DETAILS,
            cc.WHITE_ON: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
            },
        }

        return super()._translate_results_format(
            context=context,
            keymap=keymap,
            validmap=validmap,
            pinreadmap={cc.PIN, cc.PIN1, cc.PIN2},
            pinmap={cc.PIN},
            gradingcodemap=set(
                [cc.BCF_CODE],
            ),
            discardmap={
                cc.CLUB,
                cc.CLUB_CODE,
                cc.CLUB_COUNTY,
                cc.CLUB_NAME,
                cc.BCF_CODE,
                cc.BCF_NO,
                cc.FIDE_NO,
                cc.DATE_OF_BIRTH,
            },
        )

    def get_lines(self):
        """Delimiter is # optionally preceded by newline sequence."""
        filetext = []

        for f, ft in super().get_lines():
            columns = []
            row = []
            table = False
            text = []
            for t in "".join(ft).split("#"):
                ts = t.split("=", 1)
                key, value = ts[0], ts[-1]
                if key == cc.TABLE_END:
                    if row:
                        text.append(key)
                    table = False
                    columns = []
                elif key == cc.TABLE_START:
                    if table:
                        text.append(key)
                    table = True
                    row = []
                elif table:
                    if len(row) == 0:
                        row = columns[:]
                    text.append("=".join((row.pop(0), t)))
                elif key == cc.COLUMN:
                    columns.append(value)
                elif key is value:
                    text.append(key)
                else:
                    text.append("=".join((key, value)))
            filetext.append((f, text))
        return filetext

    def report_file(self, file_, text):
        """Return string containing filename and text in file."""
        end_group = {
            cc.EVENT_DETAILS,
            cc.PLAYER_LIST,
            cc.SECTION_RESULTS,
            cc.MATCH_RESULTS,
            cc.OTHER_RESULTS,
            cc.FINISH,
        }
        start_group = {cc.EVENT_CODE, cc.PIN, cc.PIN1}
        filetext = []
        linetext = []
        group = False
        for t in text:
            k = t.split("=", 1)[0]
            if k in start_group:
                if linetext:
                    filetext.append("#".join(linetext))
                linetext = [t]
                group = True
            elif k in end_group:
                if linetext:
                    filetext.append("#".join(linetext))
                linetext = []
                filetext.append(t)
                group = False
            elif group:
                linetext.append(t)
            else:
                filetext.append(t)
        if linetext:
            filetext.append("#".join(linetext))
        linetext = []

        self.filenewtextmap[file_] = "#".join(("", "\n#".join(filetext)))
        return "\n".join(
            (
                "".join((file_, "\n")),
                self.filenewtextmap[file_],
            )
        )

    def write_file(self, inpath, outpath, folder):
        """Write text derived from inpath file to outpath file in folder."""
        d = os.path.split(outpath[0])[0]
        nd = os.path.join(folder, d)
        if not os.path.exists(nd):
            os.makedirs(nd)
        with open(outpath[0], "w", encoding="utf8") as outnf:  # 'wb'?
            outnf.write(self.filenewtextmap[inpath])
            with open(
                os.path.join(nd, cc.TAKEON_ECF_FORMAT),
                "w",  # 'wb'?
                encoding="utf8",
            ) as outcf:
                del outcf

    @staticmethod
    def generate_file_name(inpath, infolder, outfolder):
        """Return file name in outfolder derived from inpath and infolder."""
        # pycodestyle E203 whitespace before ':'.
        # black formatting insists on the space.
        m = os.path.split(inpath[len(infolder) + 1 :])
        d = os.path.splitext(m[-1])
        return os.path.join(outfolder, m[0], d[0], m[-1])


class PrepareLeagueDump(PrepareResults):
    """Import data from dump of League program database."""

    def translate_results_format(self):
        """Translate results to internal format."""

        def copy_player_filter(lines, text, data):
            if cc.PCODE in data:
                if data[cc.PCODE] in self.keeppinvaluemap:
                    lines.extend(text)

        # context copied from merges.py and value part of key:value
        # changed as necessary
        context = {
            cc.LREPRESENT: None,
            cc.LCLUB: None,
            cc.LPLAYER: copy_player_filter,
            cc.LGAME: True,
            cc.LAFFILIATE: None,
            cc.LTEAM: True,
            cc.LEVENT: True,
            cc.LMATCH: True,
        }

        # keymap copied from merges.py unchanged but it could be a set here
        keymap = {
            cc.ECODE: cc.LECODE,
            cc.ENAME: cc.LENAME,
            cc.EDATE: cc.LEDATE,
            cc.EFINALDATE: cc.LEFINALDATE,
            cc.PCODE: cc.LPCODE,
            cc.PNAME: cc.LPNAME,
            cc.MCODE: cc.LMCODE,
            cc.MNAME: cc.LMNAME,
            cc.MDATE: cc.LMDATE,
            cc.PCODE1: cc.LPCODE1,
            cc.PCODE2: cc.LPCODE2,
            cc.GCODE: cc.LGCODE,
            cc.GROUND: cc.LGROUND,
            cc.GBOARD: cc.LGBOARD,
            cc.GCOLOR: cc.LGCOLOR,
            cc.GRESULT: cc.LGRESULT,
            cc.GDATE: cc.LGDATE,
            cc.MCOLOR: cc.LMCOLOR,
            cc.MTYPE: cc.LMTYPE,
            # cc.CCODE:cc.LCCODE,
            # cc.CNAME:cc.LCNAME,
            cc.TCODE: cc.LTCODE,
            cc.TNAME: cc.LTNAME,
            # cc.RPAIRING:cc.LRPAIRING,
            cc.TCODE1: cc.LTCODE1,
            cc.TCODE2: cc.LTCODE2,
            cc.PLENFORENAME: cc.LPLENFORENAME,
            cc.PLENNICKNAME: cc.LPLENNICKNAME,
        }

        # validmap copied from merges.py unchanged but it could be a set here
        validmap = {
            cc.ECODE: {cc.LEVENT: None, cc.LMATCH: None, cc.LAFFILIATE: None},
            cc.ENAME: cc.LEVENT,
            cc.EBCF: cc.LEVENT,
            cc.EDATE: {cc.LEVENT: None, cc.LAFFILIATE: None},
            cc.EFINALDATE: cc.LEVENT,
            cc.ESUBMISSION: cc.LEVENT,
            cc.ETREASURER: cc.LEVENT,
            cc.EADDRESS1: cc.LEVENT,
            cc.EADDRESS2: cc.LEVENT,
            cc.EADDRESS3: cc.LEVENT,
            cc.EADDRESS4: cc.LEVENT,
            cc.EPOSTCODE: cc.LEVENT,
            cc.EGRADER: cc.LEVENT,
            cc.EGADDRESS1: cc.LEVENT,
            cc.EGADDRESS2: cc.LEVENT,
            cc.EGADDRESS3: cc.LEVENT,
            cc.EGADDRESS4: cc.LEVENT,
            cc.EGPOSTCODE: cc.LEVENT,
            cc.EFIRSTMOVES: cc.LEVENT,
            cc.EFIRSTMINUTES: cc.LEVENT,
            cc.ENEXTMOVES: cc.LEVENT,
            cc.ENEXTMINUTES: cc.LEVENT,
            cc.ERESTMINUTES: cc.LEVENT,
            cc.EALLMINUTES: cc.LEVENT,
            cc.ESECPERMOVE: cc.LEVENT,
            cc.EADJUDICATED: cc.LEVENT,
            cc.EGRANDPRIX: cc.LEVENT,
            cc.EFIDE: cc.LEVENT,
            cc.ECHESSMOVES: cc.LEVENT,
            cc.EEAST: cc.LEVENT,
            cc.EMIDLAND: cc.LEVENT,
            cc.ENORTH: cc.LEVENT,
            cc.ESOUTH: cc.LEVENT,
            cc.EWEST: cc.LEVENT,
            cc.ECOLOR: cc.LEVENT,
            cc.CCODE: {cc.LCLUB: None, cc.LTEAM: None, cc.LAFFILIATE: None},
            cc.CNAME: cc.LCLUB,
            cc.CBCF: cc.LCLUB,
            cc.CBCFCOUNTY: cc.LCLUB,
            cc.PCODE: {
                cc.LPLAYER: None,
                cc.LAFFILIATE: None,
                cc.LREPRESENT: None,
            },
            cc.PNAME: {
                cc.LPLAYER: None,
                cc.LAFFILIATE: None,
                cc.LREPRESENT: None,
            },
            cc.PBCF: cc.LPLAYER,
            cc.PDOB: cc.LPLAYER,
            cc.PGENDER: cc.LPLAYER,
            cc.PDIRECT: cc.LPLAYER,
            cc.PTITLE: cc.LPLAYER,
            cc.PFIDE: cc.LPLAYER,
            cc.PLENFORENAME: cc.LPLAYER,
            cc.PLENNICKNAME: cc.LPLAYER,
            cc.MCODE: {cc.LMATCH: None, cc.LGAME: None},
            cc.MNAME: cc.LMATCH,
            cc.MDATE: cc.LMATCH,
            cc.MTYPE: cc.LMATCH,
            cc.MCOLOR: cc.LMATCH,
            cc.MUSEEVENTDATE: cc.LMATCH,
            cc.TCODE1: cc.LMATCH,
            cc.TCODE2: cc.LMATCH,
            cc.GROUND: cc.LGAME,
            cc.GBOARD: cc.LGAME,
            cc.GCODE: cc.LGAME,
            cc.PCODE1: cc.LGAME,
            cc.PCODE2: cc.LGAME,
            cc.GCOLOR: cc.LGAME,
            cc.GRESULT: cc.LGAME,
            cc.GDATE: cc.LGAME,
            cc.GUSEMATCHDATE: cc.LGAME,
            cc.TCODE: {cc.LTEAM: None, cc.LREPRESENT: None},
            cc.TNAME: cc.LTEAM,
            cc.RPAIRING: cc.LREPRESENT,
            cc.LREPRESENT: None,
            cc.LCLUB: None,
            cc.LPLAYER: None,
            cc.LGAME: None,
            cc.LAFFILIATE: None,
            cc.LTEAM: None,
            cc.LEVENT: None,
            cc.LMATCH: None,
        }

        # there may be PCODE values not used as PCODE1 or PCODE2 values
        # the extra _translate_results_format call with the copy_lines=False
        # argument allows the excess PCODEs to be lost.
        # PCODE1 and PCODE2 appear before PCODE in dump file. Corresponding
        # fields in submission format are other way round.
        # pinmap argument is PCODE1 and PCODE2 in mergesource.py
        super()._translate_results_format(
            context=context,
            keymap=keymap,
            validmap=validmap,
            pinreadmap={cc.PCODE, cc.PCODE1, cc.PCODE2},
            pinmap={cc.PCODE},
            gradingcodemap={cc.PBCF},
            discardmap={cc.PBCF, cc.CNAME, cc.CBCF, cc.CBCFCOUNTY},
            copy_lines=False,
        )

        return super()._translate_results_format(
            context=context,
            keymap=keymap,
            validmap=validmap,
            pinreadmap={cc.PCODE, cc.PCODE1, cc.PCODE2},
            pinmap={cc.PCODE},
            gradingcodemap={cc.PBCF},
            discardmap={cc.PBCF, cc.CNAME, cc.CBCF, cc.CBCFCOUNTY},
        )

    def report_file(self, file_, text):
        """Return string containing filename and text in file."""
        self.filenewtextmap[file_] = "\n".join(text)
        return "\n".join(
            (
                file_,
                "\n",
                self.filenewtextmap[file_],
            )
        )

    def write_file(self, inpath, outpath, folder):
        """Write text derived from inpath file to outpath file in folder."""
        d = os.path.split(outpath[0])[0]
        nd = os.path.join(folder, d)
        if not os.path.exists(nd):
            os.makedirs(nd)
        with open(outpath[0], "w", encoding="utf8") as outnf:  # 'wb'?
            outnf.write(self.filenewtextmap[inpath])
            with open(
                os.path.join(nd, cc.TAKEON_LEAGUE_FORMAT),
                "w",  # 'wb'?
                encoding="utf8",
            ) as outcf:
                del outcf

    @staticmethod
    def generate_file_name(inpath, infolder, outfolder):
        """Return path name concatenation outfolder and inpath basename.

        infolder is present for compatibility with PrepareSubmissionFile.

        """
        del infolder
        return os.path.join(
            outfolder,
            os.path.splitext(os.path.split(inpath)[-1])[0],
            cc.LEAGUE_DATABASE_DATA,
        )

    def get_folder_contents(self, container):
        """Add container to self.files set."""
        self.files.add(container)
