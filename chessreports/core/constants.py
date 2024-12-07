# constants.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Constants used in the Lite, OGD, and ECF, versions of ChessReports.

Constants shared with the ChessResultsReport version are imported from
the chessreports.core.constants module.

"""
from chessvalidate.core.constants import (
    LOSS,
    DRAWN,
    WIN,
    HWIN,
    AWIN,
    DRAW,
    HWIN_DEFAULT,
    AWIN_DEFAULT,
    DOUBLEDEFAULT,
    DRAWDEFAULT,
    HBYE,
    ABYE,
    HBYEHALF,
    ABYEHALF,
    TOBEREPORTED,
    VOID_GAME,
    NOTARESULT,
    DEFAULTED,
    TBRSTRING,
    RESULT_01,
    RESULT_55,
    RESULT_10,
    ECF_RESULT_DD,
    ECF_RESULT_1D,
    ECF_RESULT_D1,
    RECENT_EMAIL_SELECTION,
    RECENT_EMAIL_EXTRACTION,
    RECENT_CSV_DOWNLOAD,
    RECENT_DOCUMENT,
    REPORT_SECTION,
    REPORT_DAY,
    REPORT_DATE,
    REPORT_ROUND,
    REPORT_HOME_TEAM,
    REPORT_HOME_TEAM_SCORE,
    REPORT_HOME_PLAYER,
    REPORT_RESULT,
    REPORT_AWAY_PLAYER,
    REPORT_AWAY_TEAM_SCORE,
    REPORT_AWAY_TEAM,
    REPORT_BOARD,
    REPORT_HOME_PLAYER_COLOUR,
    REPORT_EVENT,
    TABULAR_REPORT_ROW_ORDER,
    FIRST_PLAYER_WHITE_PIECES,
    FIRST_PLAYER_BLACK_PIECES,
    NULL_PLAYER,
    HOME_PLAYER_WHITE,
    GRADING_ONLY,
    SECTION,
    HOME_TEAM_NAME,
    AWAY_TEAM_NAME,
    HOME_PLAYER,
    AWAY_PLAYER,
    GAME_COUNT,
    MATCH_SCORE,
    ONLY_REPORT,
    AUTHORIZATION,
    ROUND_DUP_REP,
    COMPETITION_DUP_REP,
    SOURCE_DUP_REP,
    BOARD_DUP_REP,
    RESULT_DUP_REP,
)

# Keys in <key>=<value> in data transfer files. Value ended by '\n'.
_event = "event"
_startdate = "startdate"
_enddate = "enddate"
_eventsection = "eventsection"
_eventsections = "eventsections"
_homeplayerwhite = "homeplayerwhite"
_date = "date"
_board = "board"
_round = "round"
_hometeam = "hometeam"
_awayteam = "awayteam"
_section = "section"
_sections = "sections"
_homeplayer = "homeplayer"
_homename = "homename"
_homepin = "homepin"
_homepinfalse = "homepinfalse"
_homeaffiliation = "homeaffiliation"
_homereportedcodes = "homereportedcodes"
_awayplayer = "awayplayer"
_awayname = "awayname"
_awaypin = "awaypin"
_awaypinfalse = "awaypinfalse"
_awayaffiliation = "awayaffiliation"
_awayreportedcodes = "awayreportedcodes"
_result = "result"
_name = "name"
_pin = "pin"
_pinfalse = "pinfalse"
_affiliation = "affiliation"
_exportedeventplayer = "exportedeventplayer"
_exportedplayer = "exportedplayer"
_player = "player"
_aliases = "aliases"
_newidentity = "newidentity"
_knownidentity = "knownidentity"
_sectionname = "sectionname"
_uniquesection = "uniquesection"
_serial = "serial"
_homeserial = "homeserial"
_awayserial = "awayserial"
_identified = "identified"

# To figure out team names and affiliations.
_names = "names"

# Chosen way of presenting game results in readable format.
TBR = "tbr"
AWAYDEFAULT = "1-def"  # Other 'away default' items say who won.
HOMEDEFAULT = "def-1"  # Other 'home default' items say who won.
VOID = "void"
WINBYE = "bye+"
DRAWBYE = "bye="
WHITE = "w"  # Different names because literals "WHITE" and "BLACK" exist too?
BLACK = "b"  # Should be "b" surely, but seems to have been "" for ages.
NOCOLOR = ""
WHITE_ON_ALL = "whiteonall"
BLACK_ON_ALL = "blackonall"
BLACK_ON_ODD = "blackonodd"
WHITE_ON_ODD = "whiteonodd"
COLOR_NOT_SPECIFIED = "notspecified"

# Game score identifiers on database game records.
# h... refers to first-named player usually the home player in team context.
# a... refers to second-named player usually the away player in team context.
# No assumption is made about which player has the white or black pieces.

# Commentary on printed results.

# Encoding of values used on ECF submission files.
#
# The Results File Field Definitions document (FieldDef.htm dated Oct 2006)
# reserves PIN PIN1 and PIN2 value "0" for use with results encoded by the
# SCORE values "d1" "d5" and "dd".
#
# This conflicts with the use of database record numbers as PIN PIN1 and
# PIN2 values for database engines which use 0 as a record number (after
# use of the standard conversion of integer to string).
#
# The ECF submission file generator will replace "0" by "zero_not_0" in PIN
# PIN1 and PIN2 to comply with the convention.
#
# It is hoped that this value will provide those who look at the submission
# file with a sufficient clue to what is going on: and at least assure them
# that it is not a mistake.
#
# It is also hoped that "zero_not_0" is a sufficiently unusual value that
# it will not be used by other grading programs as a valid PIN separate
# from "0".  Thus avoiding problems that may arise from the conventional
# use of "zero_not_0" by this program to cope with the ECF submission file
# conventional use of "0".
ECF_RESULT_0d = "0d"
ECF_RESULT_d0 = "d0"
ECF_COLOUR_WHITE = "white"
ECF_COLOUR_BLACK = "black"
ECF_COLOUR_W = "w"
ECF_COLOUR_B = ""
ECF_COLOURDEFAULT_ALL = "all"
ECF_COLOURDEFAULT_EVEN = "even"
ECF_COLOURDEFAULT_NONE = "none"
ECF_COLOURDEFAULT_ODD = "odd"
ECF_COLOURDEFAULT_UNKNOWN = "unknown"
ECF_ZERO_NOT_0 = "zero_not_0"

# Encoding of values used on league database extract.
result_0 = "0"
result_1 = "1"
result_2 = "2"
result_3 = "3"
result_4 = "4"
result_5 = "5"
result_6 = "6"
result_7 = "7"
result_8 = "8"
colour_0 = "0"
colour_1 = "1"
colour_2 = "2"
colourdefault_0 = "0"
colourdefault_1 = "1"
colourdefault_2 = "2"
colourdefault_3 = "3"
colourdefault_4 = "4"

# Keys used on league database extract.
ECODE = "ECODE"
ENAME = "ENAME"
EBCF = "EBCF"
EDATE = "EDATE"
EFINALDATE = "EFINALDATE"
ESUBMISSION = "ESUBMISSION"
ETREASURER = "ETREASURER"
EADDRESS1 = "EADDRESS1"
EADDRESS2 = "EADDRESS2"
EADDRESS3 = "EADDRESS3"
EADDRESS4 = "EADDRESS4"
EPOSTCODE = "EPOSTCODE"
EGRADER = "EGRADER"
EGADDRESS1 = "EGADDRESS1"
EGADDRESS2 = "EGADDRESS2"
EGADDRESS3 = "EGADDRESS3"
EGADDRESS4 = "EGADDRESS4"
EGPOSTCODE = "EGPOSTCODE"
EFIRSTMOVES = "EFIRSTMOVES"
EFIRSTMINUTES = "EFIRSTMINUTES"
ENEXTMOVES = "ENEXTMOVES"
ENEXTMINUTES = "ENEXTMINUTES"
ERESTMINUTES = "ERESTMINUTES"
EALLMINUTES = "EALLMINUTES"
ESECPERMOVE = "ESECPERMOVE"
EADJUDICATED = "EADJUDICATED"
EGRANDPRIX = "EGRANDPRIX"
EFIDE = "EFIDE"
ECHESSMOVES = "ECHESSMOVES"
EEAST = "EEAST"
EMIDLAND = "EMIDLAND"
ENORTH = "ENORTH"
ESOUTH = "ESOUTH"
EWEST = "EWEST"
ECOLOR = "ECOLOR"
CCODE = "CCODE"
CNAME = "CNAME"
CBCF = "CBCF"
CBCFCOUNTY = "CBCFCOUNTY"
PCODE = "PCODE"
PNAME = "PNAME"
PBCF = "PBCF"
PDOB = "PDOB"
PGENDER = "PGENDER"
PDIRECT = "PDIRECT"
PTITLE = "PTITLE"
PFIDE = "PFIDE"
PLENFORENAME = "PLENFORENAME"
PLENNICKNAME = "PLENNICKNAME"
MCODE = "MCODE"
MNAME = "MNAME"
MDATE = "MDATE"
MTYPE = "MTYPE"
MCOLOR = "MCOLOR"
MUSEEVENTDATE = "MUSEEVENTDATE"
TCODE1 = "TCODE1"
TCODE2 = "TCODE2"
GROUND = "GROUND"
GBOARD = "GBOARD"
GCODE = "GCODE"
PCODE1 = "PCODE1"
PCODE2 = "PCODE2"
GCOLOR = "GCOLOR"
GRESULT = "GRESULT"
GDATE = "GDATE"
GUSEMATCHDATE = "GUSEMATCHDATE"
TCODE = "TCODE"
TNAME = "TNAME"
RPAIRING = "RPAIRING"
represent = "represent"
club = "clu"
player = "player"
game = "game"
affiliate = "affiliate"
team = "team"
event = "event"
match = "match"

# Dictionary key for values extracted from submission files or league
# database extract. These keys are the same as field names on League database
# unless the value is used in the results database structure.
_ecode = ECODE
_ename = _event  # ENAME
_edate = _startdate  # EDATE
_efinaldate = _enddate  # EFINALDATE
_pcode = PCODE
_pname = _player  # PNAME
_mcode = MCODE
_mname = MNAME
_mdate = MDATE
_pcode1 = PCODE1
_pcode2 = PCODE2
_gcode = GCODE
_ground = _round  # GROUND
_gboard = _board  # GBOARD
_gcolor = GCOLOR
_gresult = _result  # GRESULT
_gdate = _date  # GDATE
_mcolor = MCOLOR
_mtype = MTYPE
_cname = CNAME
_ccode = CCODE
_tcode = TCODE
_tcode1 = TCODE1
_tcode2 = TCODE2
_tname = TNAME
_rpairing = RPAIRING
_plennickname = PLENNICKNAME
_plenforename = PLENFORENAME

# Keys used on ECF submission files.

# Those used in ECF submissions generated by this package.
EVENT_DETAILS = "EVENT DETAILS"
EVENT_CODE = "EVENT CODE"
EVENT_NAME = "EVENT NAME"
SUBMISSION_INDEX = "SUBMISSION INDEX"
EVENT_DATE = "EVENT DATE"
FINAL_RESULT_DATE = "FINAL RESULT DATE"
RESULTS_OFFICER = "RESULTS OFFICER"
RESULTS_OFFICER_ADDRESS = "RESULTS OFFICER ADDRESS"
TREASURER = "TREASURER"
TREASURER_ADDRESS = "TREASURER ADDRESS"
MOVES_FIRST_SESSION = "MOVES FIRST SESSION"
MINUTES_FIRST_SESSION = "MINUTES FIRST SESSION"
MOVES_SECOND_SESSION = "MOVES SECOND SESSION"
MINUTES_SECOND_SESSION = "MINUTES SECOND SESSION"
MINUTES_REST_OF_GAME = "MINUTES REST OF GAME"
MINUTES_FOR_GAME = "MINUTES FOR GAME"
SECONDS_PER_MOVE = "SECONDS PER MOVE"
ADJUDICATED = "ADJUDICATED"
INFORM_GRAND_PRIX = "INFORM GRAND PRIX"
INFORM_FIDE = "INFORM FIDE"
INFORM_CHESSMOVES = "INFORM CHESSMOVES"
INFORM_UNION = "INFORM UNION"
PLAYER_LIST = "PLAYER LIST"
PIN = "PIN"
BCF_CODE = "BCF CODE"
NAME = "NAME"
BCF_CODE = "BCF CODE"
CLUB = "CLUB"
CLUB_CODE = "CLUB CODE"
CLUB_COUNTY = "CLUB COUNTY"
MATCH_RESULTS = "MATCH RESULTS"
SECTION_RESULTS = "SECTION RESULTS"
OTHER_RESULTS = "OTHER RESULTS"
WHITE_ON = "WHITE ON"
PIN1 = "PIN1"
SCORE = "SCORE"
PIN2 = "PIN2"
ROUND = "ROUND"
GAME_DATE = "GAME DATE"
BOARD = "BOARD"
COLOUR = "COLOUR"
FINISH = "FINISH"

# Those available for use in ECF submissions (so merges.py must know).
RESULTS_DATE = "RESULTS DATE"
SURNAME = "SURNAME"
INITIALS = "INITIALS"
FORENAME = "FORENAME"
BCF_NO = "BCF NO"
CLUB_NAME = "CLUB NAME"
COMMENT = "COMMENT"
DATE_OF_BIRTH = "DATE OF BIRTH"
FIDE_NO = "FIDE NO"
GENDER = "GENDER"
RESULTS_DUPLICATED = "RESULTS DUPLICATED"
TITLE = "TITLE"
TABLE_END = "TABLE END"
TABLE_START = "TABLE START"
COLUMN = "COLUMN"

# Submission files earlier than about 2001 may use SURNAME FORENAME and
# INITIALS instead of NAME. Used to build PNAME if necessary.
_surname = SURNAME
_forename = FORENAME
_initials = INITIALS

# Used by control.py
_resultsdata = "games"
_ecfdata = "data"

# Used in validation of ECF codes, formerly Grading codes.
GRADING_CODE_LENGTH = 7
GRADING_CODE_CHECK_CHARACTERS = "ABCDEFGHJKL"

# Used by merges.py preparesource.py mainly.
_section_is_match = "M"
_event_matches = "Event Matches"
_yes = "yes"
_no = "no"
TAKEON_ECF_FORMAT = "takeon_ecf_format"
TAKEON_LEAGUE_FORMAT = "takeon_league_format"
TAKEON_EXT = {".txt"}
TAKEON_SCHEDULE = "takeon_schedule"
TAKEON_REPORTS = "takeon_reports"
TAKEON_MATCH_RESULTS = "#MATCH RESULTS"
TAKEON_MATCH = "match"
LEAGUE_DATABASE_DATA = "league_database_data.txt"
LEAGUE_MATCH_TYPE = "M"
TOURNAMENT_TYPE = "T"
OTHER_TYPE = "O"

# Event configuration file.
# The default extracted.conf file name defined in emailextract is not used.

# Most recently accessed database and configuation files for selecting and
# extracting text from emails to documents.
# Some could be per database, but done per user.
RECENT_DATABASE = "database"
RECENT_SUBMISSION = "submission"
RECENT_SOURCE_SUBMISSION = "source_submission"
RECENT_FEEDBACK = "feedback"
RECENT_FEEDBACK_EMAIL = "feedback_email"
RECENT_MASTERFILE = "masterfile"
RECENT_IMPORT_EVENTS = "import_events"
RECENT_EXPORT_EVENTS = "export_events"
RECENT_PERFORMANCES = "performances"
RECENT_PREDICTIONS = "predictions"
RECENT_POPULATION = "population"
RECENT_GAME_SUMMARY = "game_summary"
RECENT_EVENT_SUMMARY = "event_summary"
RECENT_GRADING_LIST = "grading_list"
RECENT_RATING_LIST = "rating_list"

# Default URLs to access ECF website.
# These are copied to a file, paired with a user, which may need editing
# if the ECF URLs change.
# PLAYER_SEARCH_URL is the 'browser searh' URL because the programming API
# does not have a 'membership number' query URL.  It is assumed a regular
# expression will be capable of locating the relevent ECF code if it exists
# in the search response.
# MEMBER_INFO_URL added when membership number query added to public API.
# (After 16 January 2022 and before 6 March 2022: too late to change v5.1.)
# Keep PLAYER_SEARCH_URL so v5.1 can work on databases accessed by v5.2.
ACTIVE_CLUBS_URL = "active_clubs_url"
PLAYERS_RATINGS_URL = "players_ratings_url"
PLAYER_INFO_URL = "player_info_url"
MEMBER_INFO_URL = "member_info_url"
CLUB_INFO_URL = "club_info_url"
PLAYER_SEARCH_URL = "player_search_url"
DEFAULT_URLS = (
    (
        ACTIVE_CLUBS_URL,
        "".join(
            (
                "https://rating.englishchess.org.uk/v2/new/",
                "api.php?v2/clubs/all_active",
            )
        ),
    ),
    (
        PLAYERS_RATINGS_URL,
        "https://rating.englishchess.org.uk/v2/new/api.php?v2/rating_list",
    ),
    (
        PLAYER_INFO_URL,
        "https://rating.englishchess.org.uk/v2/new/api.php?v2/players/code/",
    ),
    (
        MEMBER_INFO_URL,
        "https://rating.englishchess.org.uk/v2/new/api.php?v2/players/mid/",
    ),
    (
        CLUB_INFO_URL,
        "https://rating.englishchess.org.uk/v2/new/api.php?v2/clubs/code/",
    ),
    (
        PLAYER_SEARCH_URL,
        "".join(
            (
                "https://rating.englishchess.org.uk/v2/new/",
                "list_players.php?mode=A&search=",
            )
        ),
    ),
)

# ECF Grading and Rating list downloads.

# Names of the relevant columns in the ECF Grading List csv download.
# Moved from ecfogdrecord module.
ECF_OGD_PLAYERCODE_FIELD = "Ref"
ECF_OGD_PLAYERNAME_FIELD = "Name"
ECF_OGD_PLAYERCLUBS_FIELDS = (
    "ClubNam1",
    "ClubNam2",
    "ClubNam3",
    "ClubNam4",
    "ClubNam5",
    "ClubNam6",
)

# Names of the relevant columns in the ECF Rating List csv and json downloads.
# Moved from ecfogdrecord module.
ECF_ORD_PLAYERCODE_FIELD = "ECF_code"
ECF_ORD_PLAYERNAME_FIELD = "full_name"
ECF_ORD_PLAYERCLUB_FIELD = "club_name"
ECF_ORD_PLAYERCLUBS_FIELDS = (ECF_ORD_PLAYERCLUB_FIELD,)


# Structure of ECF json downloads.
A_C_CLUBS = "clubs"
ACTIVE_CLUBS_KEYS = frozenset(
    [
        A_C_CLUBS,
        "success",
        "processing_time",
        "total_processing_time_today",
        "max_processing_time_daily",
    ]
)
# gui.ecf.activeclubs will need updating if row key names in the download are
# changed in future and a new dated version of this tuple is added.
ACTIVE_CLUBS_ROW_KEY_NAMES = (
    "club_code",
    "club_name",  # Do not assume it is same name as in rating download.
    "comment",
    "assoc_code",
    "assoc_name",
)
ACTIVE_CLUBS_ROW_KEY_TUPLES = (ACTIVE_CLUBS_ROW_KEY_NAMES,)
P_R_COLUMN_NAMES = "column_names"
P_R_PLAYERS = "players"
PLAYERS_RATINGS_KEYS = frozenset(
    [
        "rating_effective_date",
        P_R_COLUMN_NAMES,
        P_R_PLAYERS,
        "success",
        "processing_time",
        "total_processing_time_today",
        "max_processing_time_daily",
    ]
)
# gui.ecf.control will need updating if column names in the download are
# changed in future and a new dated version of this tuple is added.
PLAYERS_RATINGS_COLUMN_NAMES_ORIGINAL = (
    ECF_ORD_PLAYERCODE_FIELD,
    ECF_ORD_PLAYERNAME_FIELD,
    "member_no",
    "FIDE_no",
    "gender",
    "nation",
    "original_standard",
    "revised_standard",
    "standard_category",
    "original_rapid",
    "revised_rapid",
    "rapid_category",
    "original_standard_online",
    "revised_standard_online",
    "original_rapid_online",
    "revised_rapid_online",
    "original_blitz_online",
    "revised_blitz_online",
    "club_code",
    ECF_ORD_PLAYERCLUB_FIELD,
)
# gui.ecf.control will need updating if column names in the download are
# changed in future and a new dated version of this tuple is added.
PLAYERS_RATINGS_COLUMN_NAMES_2022_10 = (
    ECF_ORD_PLAYERCODE_FIELD,
    ECF_ORD_PLAYERNAME_FIELD,
    "member_no",
    "FIDE_no",
    "gender",
    "nation",
    "original_standard",
    "standard_original_category",
    "revised_standard",
    "standard_revised_category",
    "original_rapid",
    "rapid_original_category",
    "revised_rapid",
    "rapid_revised_category",
    "original_blitz",
    "blitz_original_category",
    "revised_blitz",
    "blitz_revised_category",
    "original_standard_online",
    "standard_online_original_category",
    "revised_standard_online",
    "standard_online_revised_category",
    "original_rapid_online",
    "rapid_online_original_category",
    "revised_rapid_online",
    "rapid_online_revised_category",
    "original_blitz_online",
    "blitz_online_original_category",
    "revised_blitz_online",
    "blitz_online_revised_category",
    "club_code",
    ECF_ORD_PLAYERCLUB_FIELD,
)
PLAYERS_RATINGS_COLUMN_COUNTS = (
    len(PLAYERS_RATINGS_COLUMN_NAMES_ORIGINAL),
    len(PLAYERS_RATINGS_COLUMN_NAMES_2022_10),
)
# Names of columns in tabular game reports generated by ChessReports.
# These are not used by emailextractor module which defines names of entries
# in the extract text configuration file which name the columns.
# The constants defined here are REPORT_SECTION, and so forth, while the
# constants in emailextractor are _REPORT_SECTION, and so forth.

# Suitable for sorting rows into order for easy eyeball inspection.

# Suitable for generating parsable " ".join(row) from csv file.
# ECF code and ECF membership number should be prefixes to the player name
# in REPORT_HOME_PLAYER, and suffixes in REPORT_AWAY_PLAYER, if they are
# reported to avoid confusion if only one player has these.

# Display value for side indicator in game records and structures.

# Problem indicators for duplicate game reports.
# Some have suffix _DUP_REP because at least one other constant had the
# same name originally, defined in another module.
