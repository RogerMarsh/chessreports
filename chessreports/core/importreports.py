# importreports.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Extract results from a file in this applications export format."""
from chessvalidate.core.gameresults import displayresult

from . import constants


def get_event_from_player(p):
    """Return event identifier from player identifier."""
    return (
        p[1],
        p[2],
        p[3],
    )


def convert_alias_to_transfer_format(alias, cname):
    """Convert alias to key=value strings and return in a list.

    alias must be in format returned by resultsrecord.get_alias_identity

    """
    outputdata = [
        "=".join((constants.EVENT, alias[3])),
        "=".join((constants.STARTDATE, alias[1])),
        "=".join((constants.ENDDATE, alias[2])),
    ]
    for s in alias[4]:
        outputdata.append("=".join((constants.EVENTSECTION, s)))
    if alias[5]:
        outputdata.append("=".join((constants.SECTION, alias[5])))
    if alias[6]:
        outputdata.append("=".join((constants.PIN_LOWER, str(alias[6]))))
    elif alias[6] is False:
        outputdata.append("=".join((constants.PINFALSE, "true")))
    outputdata.append("=".join((cname, alias[0])))
    return outputdata


def get_player_identifier(
    data,
    player=constants.NAME_LOWER,
    pin=constants.PIN_LOWER,
    section=constants.SECTION,
):
    """Return player identifier tuple from data details.

    Returned tuple format is:

    Player name
    Event name
    Event start date
    Event end date
    Name of club played for in event or event section played in or None
    None for club name or player's PIN, or False, in event section or None

    On the database the three event items are used as the identity of an event
    record.  Event and club or section names are replaced by record keys in
    a player identity.  Event section names are replaced by record keys on
    event records.

    Player identity is: Player name, Event key, Club or section key, pin value

    """
    if data[pin] is not None:
        return (
            data[player],
            data[constants.EVENT],
            data[constants.STARTDATE],
            data[constants.ENDDATE],
            data[constants.SECTION],
            data[pin],
        )
    if section is not constants.SECTION:  # data[section] is not None?
        return (
            data[player],
            data[constants.EVENT],
            data[constants.STARTDATE],
            data[constants.ENDDATE],
            data[section],
            None,
        )
    return (
        data[player],
        data[constants.EVENT],
        data[constants.STARTDATE],
        data[constants.ENDDATE],
        None,
        None,
    )


class ImportReports:
    """Class for importing results data."""

    def __init__(self, textlines):
        """Initialise for import report of results in textlines."""
        super().__init__()
        self.textlines = textlines
        self.game = {}
        self.gameplayer = set()
        self.localplayer = {}  # set()
        self.gameplayermerge = {}
        self.remoteplayer = {}
        self.new_to_known = {}
        self.known_to_new = {}
        self.localevents = {}
        self.remoteevents = {}
        self.newevents = {}
        self.knownevents = {}
        self._newidentifier = None
        self.error = []

    def translate_results_format(self):
        """Extract result and player identification data."""

        def translate_data(items, translateitems):
            for k in data:
                if k not in items:
                    return False
            for k, v in translateitems.items():
                if k in data:
                    if v in data:
                        return False
                    if data[k]:
                        data[v] = False
                    del data[k]
                elif v in data:
                    data[v] = int(data[v])
            for k, v in items.items():
                if k not in data:
                    if v is True:
                        return False
                    if v is False:
                        continue
                    data[k] = v
            for v in datalistitems.values():
                if v in data:
                    # data[v] can be None for reported codes.
                    # Possibly should be fixed upstream: data[v] = ()
                    if data[v] is not None:
                        data[v] = tuple(sorted(data[v]))
                    else:
                        data[v] = ()

            return True

        def game():
            if not translate_data(gameitems, translategameitems):
                return False
            if (
                data[constants.RESULT] not in displayresult
            ):  # constants._storeresults:
                return False
            for name, pin, affiliation in (
                (
                    constants.HOMENAME,
                    constants.HOMEPIN,
                    constants.HOMEAFFILIATION,
                ),
                (
                    constants.AWAYNAME,
                    constants.AWAYPIN,
                    constants.AWAYAFFILIATION,
                ),
            ):
                identity = get_player_identifier(
                    data, player=name, pin=pin, section=affiliation
                )
                if identity not in self.gameplayer:
                    self.gameplayer.add(identity)
            gamenumber = len(self.game)
            self.game[gamenumber] = data.copy()
            data.clear()
            return True

        def get_event_identifier():
            """Return event identifier from data details."""
            return (
                data[constants.EVENT],
                data[constants.STARTDATE],
                data[constants.ENDDATE],
            )

        def get_player_key(player):
            """Return player key from data details for import name matching.

            The names placed on the export file for matching names between
            two databases use section and pin for all qualifiers of player
            name.  Generates same key as get_player_identifier but source
            of key elements does not vary.
            """
            return (
                data[player],
                data[constants.EVENT],
                data[constants.STARTDATE],
                data[constants.ENDDATE],
                data[constants.SECTION],
                data[constants.PIN_LOWER],
            )

        def known_player():
            if self._newidentifier is None:
                return False
            if not translate_data(knownplayeritems, translateknownplayeritems):
                return False
            merge_event_sections(self.knownevents)
            known = get_player_key(constants.KNOWNIDENTITY)
            if known in self.known_to_new:
                return False
            self.map_known_to_new(known, self._newidentifier)
            self._newidentifier = None
            data.clear()
            return True

        def new_player():
            if self._newidentifier is not None:
                return False
            if not translate_data(newplayeritems, translatenewplayeritems):
                return False
            merge_event_sections(self.newevents)
            self._newidentifier = get_player_key(constants.NEWIDENTITY)
            data.clear()
            return True

        def merge_local_players():
            for k in data:
                if k not in mergeplayeritems:
                    return False
            if merges:
                player = merges[-1]
                self.localplayer[player] = set(merges)
                for m in merges:
                    self.gameplayermerge[m] = player
            data.clear()
            merges[:] = []
            return True

        def merge_remote_players():
            for k in data:
                if k not in mergeremoteplayeritems:
                    return False
            if merges:
                aliases = data[constants.ALIASES]
                player = merges.pop()
                m = set(merges)
                if len(m) != len(merges):
                    return False
                self.remoteplayer[player] = (aliases, m)
                for p in merges:
                    self.remoteplayer[p] = (None, player)
            data.clear()
            merges[:] = []
            return True

        def players_on_export_database():
            for k in data:
                if k not in notmergeplayeritems:
                    return False
            data.clear()
            merges[:] = []
            return True

        def remote_player():
            if not translate_data(
                remoteplayeritems, translateremoteplayeritems
            ):
                return False
            merge_event_sections(self.remoteevents)
            identity = get_player_key(constants.PLAYER)
            if identity in self.remoteplayer:
                data.clear()
                return True
            merges.append(identity)
            data.clear()
            return True

        def local_player():
            if not translate_data(playeritems, translateplayeritems):
                return False
            merge_event_sections(self.localevents)
            identity = get_player_key(constants.NAME_LOWER)
            if identity in self.localplayer:
                return False
            merges.append(identity)
            self.localplayer[identity] = None
            data.clear()
            return True

        def games_finished():
            for key in constants.RESULT, constants.PIN_LOWER:
                del context[key]
            context[constants.IDENTIFIED] = remote_players_finished
            return True

        def local_players_finished():
            for key in (
                constants.EXPORTEDEVENTPLAYER,
                constants.EXPORTEDPLAYER,
                constants.NAME_LOWER,
                constants.HOMEPLAYERWHITE,
            ):
                del context[key]
            context[constants.PIN_LOWER] = games_finished
            context[constants.IDENTIFIED] = remote_players_finished
            return True

        def ignore_merge_instructions():
            # Ignore the merge instructions appended by this module after
            # receipt of response from destination system requesting player
            # identification.
            # In other words ignore data after validating structure while
            # avoiding the data error condition.
            data.clear()
            return True

        def merge_event_sections(events):
            e = get_event_identifier()
            es = events.setdefault(e, set())
            es.update(data[constants.EVENTSECTIONS])

        def remote_players_finished():
            for k in data:
                if k != constants.IDENTIFIED:
                    return False
            for key in (
                constants.PLAYER,
                constants.ALIASES,
                constants.IDENTIFIED,
            ):
                del context[key]
            context[constants.KNOWNIDENTITY] = known_player
            context[constants.NEWIDENTITY] = new_player
            context[constants.ALIASES] = ignore_merge_instructions
            data.clear()
            return True

        context = {
            constants.RESULT: game,
            constants.NAME_LOWER: local_player,
            constants.PLAYER: remote_player,
            constants.EXPORTEDEVENTPLAYER: merge_local_players,
            constants.EXPORTEDPLAYER: players_on_export_database,
            constants.HOMEPLAYERWHITE: local_players_finished,
            constants.ALIASES: merge_remote_players,
        }

        datalistitems = {
            constants.EVENTSECTION: constants.EVENTSECTIONS,
            constants.HOMEREPORTEDCODES: constants.HOMEREPORTEDCODES,
            constants.AWAYREPORTEDCODES: constants.AWAYREPORTEDCODES,
        }

        inputitems = {
            constants.STARTDATE,
            constants.ENDDATE,
            constants.EVENT,
            constants.EVENTSECTION,
            constants.SECTION,
            constants.DATE,
            constants.HOMEPLAYERWHITE,
            constants.HOMENAME,
            constants.AWAYNAME,
            constants.HOMEPIN,
            constants.AWAYPIN,
            constants.HOMEAFFILIATION,
            constants.AWAYAFFILIATION,
            constants.HOMEREPORTEDCODES,
            constants.AWAYREPORTEDCODES,
            constants.RESULT,
            constants.HOMETEAM,
            constants.AWAYTEAM,
            constants.BOARD_LOWER,
            constants.ROUND_LOWER,
            constants.HOMEPINFALSE,
            constants.AWAYPINFALSE,
            constants.NAME_LOWER,
            constants.PIN_LOWER,
            constants.PINFALSE,
            constants.AFFILIATION,
            constants.EXPORTEDEVENTPLAYER,
            constants.EXPORTEDPLAYER,
            constants.PLAYER,
            constants.ALIASES,
            constants.NEWIDENTITY,
            constants.KNOWNIDENTITY,
            constants.IDENTIFIED,
        }

        gameitems = {
            constants.STARTDATE: True,
            constants.ENDDATE: True,
            constants.EVENT: True,
            constants.EVENTSECTIONS: True,
            constants.SECTION: None,
            constants.DATE: True,
            constants.HOMEPLAYERWHITE: True,
            constants.HOMENAME: True,
            constants.AWAYNAME: True,
            constants.HOMEPIN: None,
            constants.AWAYPIN: None,
            constants.HOMEAFFILIATION: None,
            constants.AWAYAFFILIATION: None,
            constants.HOMEREPORTEDCODES: None,
            constants.AWAYREPORTEDCODES: None,
            constants.RESULT: True,
            constants.HOMETEAM: None,
            constants.AWAYTEAM: None,
            constants.BOARD_LOWER: None,
            constants.ROUND_LOWER: None,
            constants.HOMEPINFALSE: False,
            constants.AWAYPINFALSE: False,
        }

        mergeremoteplayeritems = {
            constants.ALIASES: True,
        }

        newplayeritems = {
            constants.STARTDATE: True,
            constants.ENDDATE: True,
            constants.EVENT: True,
            constants.EVENTSECTIONS: True,
            constants.SECTION: None,
            constants.NEWIDENTITY: True,
            constants.PIN_LOWER: None,
            constants.PINFALSE: False,
        }

        knownplayeritems = {
            constants.STARTDATE: True,
            constants.ENDDATE: True,
            constants.EVENT: True,
            constants.EVENTSECTIONS: True,
            constants.SECTION: None,
            constants.KNOWNIDENTITY: True,
            constants.PIN_LOWER: None,
            constants.PINFALSE: False,
        }

        mergeplayeritems = {
            constants.EXPORTEDEVENTPLAYER: True,
        }

        notmergeplayeritems = {
            constants.EXPORTEDPLAYER: True,
        }

        playeritems = {
            constants.STARTDATE: True,
            constants.ENDDATE: True,
            constants.EVENT: True,
            constants.EVENTSECTIONS: True,
            constants.SECTION: None,
            constants.NAME_LOWER: True,
            constants.PIN_LOWER: None,
            constants.PINFALSE: False,
        }

        remoteplayeritems = {
            constants.STARTDATE: True,
            constants.ENDDATE: True,
            constants.EVENT: True,
            constants.EVENTSECTIONS: True,
            constants.SECTION: None,
            constants.PLAYER: True,
            constants.PIN_LOWER: None,
            constants.PINFALSE: False,
        }

        translategameitems = {
            constants.HOMEPINFALSE: constants.HOMEPIN,
            constants.AWAYPINFALSE: constants.AWAYPIN,
        }

        translateknownplayeritems = {
            constants.PINFALSE: constants.PIN_LOWER,
        }

        translatenewplayeritems = {
            constants.PINFALSE: constants.PIN_LOWER,
        }

        translateremoteplayeritems = {
            constants.PINFALSE: constants.PIN_LOWER,
        }

        translateplayeritems = {
            constants.PINFALSE: constants.PIN_LOWER,
        }

        data = {}
        merges = []
        for e, t in enumerate(self.textlines):
            ts = t.split("=", 1)
            key, value = ts[0], ts[-1]
            if key not in inputitems:
                if len(key) != 0:
                    self.error = ["Unknown field name", e, t]
                    return False
            if key in datalistitems:
                data.setdefault(datalistitems[key], set()).add(value)
            else:
                data[key] = value
            if key in context:
                if not context[key]():
                    self.error = ["Field processing error", e, t]
                    return False
        if len(data):
            self.error = ["Unprocessed data", len(self.textlines), ""]
            return False
        if self._newidentifier is not None:
            self.error = ["Not new identifier", len(self.textlines), ""]
            return False
        return True

    def is_reply_consistent_with_request(self, request):
        """Return True if self consistent with request, otherwise False.

        Assumed that self is reply to an identification request and
        request is the response to the original import.

        """
        if self is request:
            return False
        # quick check that reply can be consistent with request.
        # element comparisons below include this check.
        if len(self.game) != len(request.game):
            return False
        if len(self.gameplayer) != len(request.gameplayer):
            return False
        if len(self.localplayer) != len(request.localplayer):
            return False
        if len(self.gameplayermerge) != len(request.gameplayermerge):
            return False
        if len(self.remoteplayer) != len(request.remoteplayer):
            return False
        # cannot be request or reply if remoteplayer empty
        # (except for trivial case of import applied to empty database)
        # (in which case there is nothing to do)
        if len(self.remoteplayer) == 0:
            return False
        if len(request.remoteplayer) == 0:
            return False
        if len(request.new_to_known) != 0:
            return False
        if len(request.known_to_new) != 0:
            return False
        if len(self.new_to_known) == 0:
            return False
        if len(self.known_to_new) == 0:
            return False
        # check for equality of self and request sub-states
        for rep, req in ((self.gameplayer, request.gameplayer),):
            for k in rep:
                if k not in req:
                    return False
                req.remove(k)
            if len(req) != 0:
                return False
        for rep, req in (
            (self.game, request.game),
            (self.gameplayermerge, request.gameplayermerge),
            (self.localplayer, request.localplayer),
            (self.remoteplayer, request.remoteplayer),
        ):
            for k, v in rep.items():
                if k not in req:
                    return False
                if v != req[k]:
                    return False
                del req[k]
            if len(req) != 0:
                return False
        return True

    def get_event_names(self):
        """Return sorted list of event names."""
        return sorted({p[1:4] for p in self.gameplayer})

    def get_new_players(self):
        """Return set of new players according to importing database."""
        discard = set()
        for nps in self.known_to_new.values():
            discard.update(nps)
        new_players = self.gameplayer - discard
        discard = set()
        for p in new_players:
            if p not in self.remoteplayer:
                discard.add(p)
            elif p in self.new_to_known:
                discard.add(p)
            else:
                merge, alias = self.remoteplayer[p]
                if merge is None:
                    merge, alias = self.remoteplayer[alias]
                if merge == "False":
                    discard.add(p)
        new_players.difference_update(discard)
        return new_players

    def map_known_to_new(self, knownplayer, newplayer):
        """Add new player to known player map."""
        self.new_to_known[newplayer] = knownplayer
        self.known_to_new[knownplayer] = self.localplayer[
            self.gameplayermerge[newplayer]
        ]

    def get_game_players(self):
        """Return dictionary mapping gameplayers to aliases."""
        gameplayer = self.gameplayer
        gameplayermerge = self.gameplayermerge
        localplayer = self.localplayer
        players = {}
        for gp in gameplayer:
            gpm = gameplayermerge[gp]
            if gpm in gameplayer:  # is exporter main alias used in games
                if gpm not in players:
                    players[gpm] = set()
                if gpm != gp:
                    players[gpm].add(gp)
            else:
                for p in localplayer[gpm]:
                    if p in players:  # is any exporter alias already found
                        players[p].add(gp)
                        break
                else:  # use this alias as importers main alias
                    players[gp] = set()
        return players


def get_import_event_reports(data):
    """Return an ImportReports instance for data."""
    importdata = ImportReports(data)
    if importdata.translate_results_format():
        return importdata
    return None
