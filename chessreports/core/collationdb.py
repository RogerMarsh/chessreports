# collationdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Database update for collated reported results.

A separate class is used because it is reasonable to use the Collation class
without database support for the collation data.

The collated results from the results report replace any existing results on
the database for the reported events.

"""
from chessvalidate.core.gameresults import ecfresult
from chessvalidate.core.gameobjects import (
    Game,
    SwissMatchGame,
    SwissGame,
    MatchGame,
    MatchReport,
)

from .resultsrecord import ResultsDBrecordEvent, ResultsDBrecordGame
from .resultsrecord import ResultsDBrecordName, ResultsDBrecordPlayer
from .resultsrecord import get_alias, get_name_from_record_value
from .resultsrecord import get_events_matching_event_identity
from .resultsrecord import get_games_for_event, get_affiliation_details
from . import filespec


class CollationDB:
    """Update results database from games in a Collation instance."""

    def __init__(self, games, database):
        """Note the games and database to be updated.

        games - the games containing results to apply to database
        database - the ResultsDatabase instance for the database to be updated

        """
        self._games = games
        self._database = database

    def update_results(self):
        """Apply games to database replacing existing games for event.

        Caller is responsible for commit or backout action.

        """
        eventsections = {}  # {name : {section name : srkey, ...}, ...}
        eventsamend = {}
        eventskey = {}  # {srkey : name, ...}
        eventsmap = {}  # {name : srkey, ...}
        namemanager = NameManager(self._database)
        players = {}  # {srkey: ResultsDBrecordPlayer instance, ...}
        playersamend = {}
        playersgames = {}
        playerskey = {}
        playersmap = {}
        new_players = {}
        newgames = []  # [ResultsDBrecordGame instance, ...]
        newgamesmap = {}  # [instance attributes tuple : count, ...}
        dbgames = []  # [ResultsDBrecordGame instance, ...]
        dbgamesmap = {}  # [instance attributes tuple : [key, ...], ...}
        merges = {}  # {key: ResultsDBrecordPlayer instance, ...}
        mergesamend = {}

        def get_players_blocking_update(buplayers):
            """Return players with merges or ECF codes blocking update."""
            ret = []
            for bup in buplayers:
                affiliation = get_affiliation_details(
                    self._database, players[bup].value.affiliation
                )
                name, event, start, end, section, pin = bup
                if section is None:
                    section = ""
                if pin is None:
                    pin = ""
                if affiliation is None:
                    affiliation = ""
                ret.append(
                    "\t".join(
                        (
                            name,
                            "  ".join((start, end, event)),
                            get_name_from_record_value(
                                self._database.get_primary_record(
                                    filespec.NAME_FILE_DEF, section
                                )
                            ).value.name,
                            str(pin),
                            affiliation,
                        )
                    )
                )
            return "\n".join(ret)

        def set_name_list(namelist):
            """Return list of name keys for names."""
            namekeys = []
            for n in namelist:
                namekeys.append(namemanager.set_name(n))
            return namekeys

        def set_player(player):
            """Create record for new player and prepare amendments."""
            pid = player.get_identity()
            affiliation = player.affiliation
            if pid not in new_players:
                name, event, start, end, section, pin = pid
                if section is not None:
                    namemanager.set_name(section)
                if affiliation:
                    namemanager.set_name(affiliation)
                new_players[pid] = None
            if pid not in players:
                pr = ResultsDBrecordPlayer()
                pr.value.name = name
                pr.value.event = eventsmap[(event, start, end)]
                if pin is not None:
                    pr.value.section = namemanager.get_code(section)
                elif section is not None:
                    pr.value.section = namemanager.get_code(section)
                pr.value.pin = pin
                pr.value.reported_codes = list(player.reported_codes)
                if affiliation:
                    pr.value.affiliation = namemanager.get_code(affiliation)
                pr.key.recno = None
                pr.put_record(self._database, filespec.PLAYER_FILE_DEF)
                players[pid] = pr
                playerskey[pr.key.recno] = pid
                playersmap[pid] = pr.key.recno
            else:
                change_affiliation = False
                if not affiliation:
                    if players[pid].value.affiliation:
                        change_affiliation = True
                        new_affiliation = None
                elif (
                    namemanager.get_code(affiliation)
                    != players[pid].value.affiliation
                ):
                    change_affiliation = True
                    new_affiliation = namemanager.get_code(affiliation)
                change_reported_codes = (
                    set(players[pid].value.reported_codes)
                    != player.reported_codes
                )
                if change_affiliation or change_reported_codes:
                    if pid not in playersamend:
                        playersamend[pid] = players[pid].clone()
                        if change_affiliation:
                            playersamend[pid].value.affiliation = (
                                new_affiliation
                            )
                        if change_reported_codes:
                            playersamend[pid].value.reported_codes = list(
                                player.reported_codes
                            )
            playersgames[pid] = True

        def unset_player(skey):
            """Decrement affiliation and section counts and create key maps."""
            if skey not in playerskey:
                pr = get_alias(self._database, skey)
                a = pr.value.affiliation
                if a is not None:
                    namemanager.unset_name(a)
                pe = eventskey[pr.value.event]
                if pr.value.section:
                    ps = namemanager.unset_name(pr.value.section)
                else:
                    ps = pr.value.section
                pid = (
                    pr.value.name,
                    pe.value.name,
                    pe.value.startdate,
                    pe.value.enddate,
                    ps,
                    pr.value.pin,
                )
                playerskey[skey] = pid
                playersmap[pid] = skey
                players[pid] = pr
                playersgames[pid] = False

        # Get new events.
        for ugkey in self._games:
            competition = self._games[ugkey].competition
            for game in self._games[ugkey].games:
                if isinstance(game, Game):
                    if (
                        game.homeplayer is None
                        or game.awayplayer is None
                        or game.result not in ecfresult
                    ):
                        continue
                    if game.gradegame is not True:  # only test eventually.
                        continue
                else:
                    continue
                hp = game.homeplayer
                event_id = (hp.event, hp.startdate, hp.enddate)
                if event_id not in eventsections:
                    eventsections[event_id] = {}
                if competition not in eventsections[event_id]:
                    eventsections[event_id][competition] = None

        # Get existing events and match with new events if possible.
        # Note that the database may contain several event records for
        # each key in events. Any of these that intersect the new events
        # using competition will be replaced by a single record.
        # Pick one of the existing event records for each event to become
        # the event record used for the replacement results. Arbitrary choice
        # now but possibly the event with most games is better.
        delete_events = []
        use_events = []
        for eskey, esvalue in eventsections.items():
            sections = list(esvalue.keys())
            dbevents = get_events_matching_event_identity(
                self._database, eskey
            )
            replace_events = []
            for key, value in dbevents.items():
                dbsections = {}
                for s in value.value.sections:
                    dbsections[
                        get_name_from_record_value(
                            self._database.get_primary_record(
                                filespec.NAME_FILE_DEF, s
                            )
                        ).value.name
                    ] = None
                for s in sections:
                    if s in dbsections:
                        replace_events.append((key, eskey, value))
                        srdbe = value.key.recno
                        eventsmap[eskey] = srdbe
                        eventskey[srdbe] = value
                        eventsamend[srdbe] = value.clone()
                        for es in sections:
                            esvalue[es] = srdbe
                        break
            if replace_events:
                use_events.append(replace_events.pop())
            delete_events.extend(replace_events)
            del replace_events

        # Get names used by existing events and decrement reference counts
        # Get players involved in existing games and decrement reference
        # counts for names used by these games and players. Invert the
        # value dictionary for comparison with new games.
        for dbevents in (delete_events, use_events):
            for item in dbevents:
                record = item[2]
                for s in record.value.sections:
                    namemanager.unset_name(s)
                for g in get_games_for_event(self._database, record):
                    for s in (
                        g.value.awayteam,
                        g.value.hometeam,
                        g.value.section,
                    ):
                        if s is not None:
                            namemanager.unset_name(s)
                    for p in (g.value.homeplayer, g.value.awayplayer):
                        unset_player(p)
                    ig = []
                    d = g.value.__dict__
                    # Replace with 'ig = literal_eval(g.value.pack_value())'
                    # pylint: disable-next=protected-access
                    for a in g.value._attribute_order:
                        ig.append(d[a])
                    igt = tuple(ig)
                    if igt in dbgamesmap:
                        dbgamesmap[igt].append(g)
                    else:
                        dbgamesmap[igt] = [g]
        del use_events

        # Go through new games to find players that already exist on database.
        # If any missing from new games have aliases that are not being deleted
        # the update cannot proceed.
        # (Check if aliases are in dbplayers as well.)
        dbplayers = {}
        dbplayerskey = {}
        for key, value in players.items():
            dbplayers[key] = None
            dbplayerskey[value.key.recno] = key
        for ugkey in self._games:
            collation = self._games[ugkey]
            competition = collation.competition
            for game in collation.games:
                if isinstance(game, Game):
                    if (
                        game.homeplayer is None
                        or game.awayplayer is None
                        or game.result not in ecfresult
                    ):
                        continue
                    if game.gradegame is not True:  # only test eventually.
                        continue
                else:
                    continue
                for p in (game.homeplayer, game.awayplayer):
                    pid = p.get_identity()
                    if pid in dbplayers:
                        del dbplayers[pid]
                        del dbplayerskey[players[pid].key.recno]
        dbplayersdict = {}
        for pid in dbplayers:
            for a in players[pid].value.get_alias_list():
                if a not in dbplayerskey:
                    dbplayersdict[pid] = None
                    break
        if len(dbplayersdict):
            return (
                "".join(
                    (
                        "Demerge listed players and Identify using an ",
                        "entry that is not being deleted.  Such entries ",
                        "are not in this list.",
                    )
                ),
                get_players_blocking_update(dbplayersdict),
            )
        del dbplayers
        del dbplayersdict

        # Put new events (no existing event records) in event map. Use an
        # existing event record if one is available.
        for key, value in eventsections.items():
            if key not in eventsmap:
                er = ResultsDBrecordEvent()
                er.value.name, er.value.startdate, er.value.enddate = key
                er.value.sections = set_name_list(list(value.keys()))
                er.key.recno = None
                er.put_record(self._database, filespec.EVENT_FILE_DEF)
                eventsmap[key] = er.key.recno
                for s in value:
                    value[s] = er.key.recno
            else:
                snl = set_name_list(list(value.keys()))
                if eventsmap[key] in eventsamend:
                    eventsamend[eventsmap[key]].value.sections[:] = snl

        # Create new name and player records for new games.
        for ugkey in self._games:
            collation = self._games[ugkey]
            competition = collation.competition
            matchreport = isinstance(collation, MatchReport)
            for game in collation.games:
                if isinstance(game, Game):
                    if (
                        game.homeplayer is None
                        or game.awayplayer is None
                        or game.result not in ecfresult
                    ):
                        continue
                    if game.gradegame is not True:  # only test eventually.
                        continue
                else:
                    continue
                namemanager.set_name(competition)
                for p in (game.homeplayer, game.awayplayer):
                    set_player(p)
                if matchreport:
                    for team in (collation.hometeam, collation.awayteam):
                        if team is not None:
                            namemanager.set_name(team)

        # Adjust associated player records where a merged player record is
        # deleted. Use instances in players if available. Create instances in
        # merges if necessary.
        for key, value in players.items():
            if not playersgames[key]:
                m = value.value.merge
                if m is False:
                    continue
                if m is None:
                    continue
                if m in dbplayerskey:
                    if dbplayerskey[m] not in playersamend:
                        continue
                    adjustmerge = playersamend[dbplayerskey[m]]
                elif m in merges:
                    adjustmerge = mergesamend[m]
                else:
                    pr = get_alias(self._database, m)
                    merges[m] = pr
                    mergesamend[m] = merges[m].clone()
                    adjustmerge = mergesamend[m]
                try:
                    adjustmerge.value.alias.remove(value.key.recno)
                except ValueError:
                    pass

        # Prepare new games and invert the value dictionary for comparison
        # with games from database.
        for ugkey in self._games:
            collation = self._games[ugkey]
            competition_date = collation.date
            competition = collation.competition
            for game in collation.games:
                if isinstance(game, Game):
                    if (
                        game.homeplayer is None
                        or game.awayplayer is None
                        or game.result not in ecfresult
                    ):
                        continue
                    if game.gradegame is not True:  # only test eventually.
                        continue
                else:
                    continue
                gr = ResultsDBrecordGame()
                gr.key.recno = None
                gr.value.homeplayer = playersmap[
                    game.homeplayer.get_identity()
                ]
                gr.value.awayplayer = playersmap[
                    game.awayplayer.get_identity()
                ]
                gr.value.homeplayerwhite = game.homeplayerwhite
                gr.value.result = game.result
                if game.date:
                    gr.value.date = game.date
                elif competition_date:
                    gr.value.date = competition_date
                else:
                    gr.value.date = game.homeplayer.startdate
                gr.value.board = None
                gr.value.round = None
                if isinstance(game, SwissMatchGame):
                    gr.value.board = game.board
                    gr.value.round = game.round
                if isinstance(game, SwissGame):
                    gr.value.round = game.round
                if isinstance(game, MatchGame):
                    gr.value.board = game.board
                gr.value.event = eventsections[
                    game.homeplayer.get_player_event()
                ][competition]
                gr.value.section = namemanager.get_code(competition)
                if isinstance(collation, MatchReport):
                    gr.value.hometeam = namemanager.get_code_default(
                        collation.hometeam
                    )
                    gr.value.awayteam = namemanager.get_code_default(
                        collation.awayteam
                    )
                else:
                    gr.value.hometeam = None
                    gr.value.awayteam = None
                ig = []
                d = gr.value.__dict__
                # Replace with 'ig = literal_eval(gr.value.pack_value())'
                # pylint: disable-next=protected-access
                for a in gr.value._attribute_order:
                    ig.append(d[a])
                igt = tuple(ig)
                if igt in newgamesmap:
                    newgamesmap[igt].append(gr)
                else:
                    newgamesmap[igt] = [gr]
        for ngm in list(newgamesmap.keys()):
            if ngm in dbgamesmap:
                minlen = min(len(newgamesmap[ngm]), len(newgamesmap[ngm]))
                del newgamesmap[ngm][:minlen]
                del dbgamesmap[ngm][:minlen]
        for ngm in newgamesmap.values():
            newgames.extend(ngm)
        for dgm in dbgamesmap.values():
            dbgames.extend(dgm)

        # Check that player records being deleted are not ones used to link
        # to ECF grading code records.
        # It is assumed no player deletions occur for new events, so the
        # earlier put_record for a new event will not have happened.
        # Note it may be possible to do something sensible in all cases.
        linkers = []
        for key, value in players.items():
            if not playersgames[key]:
                if value.value.merge is False:
                    linkers.append(value.value.name)
        if linkers:
            return (
                "".join(
                    (
                        "These player's records cannot be deleted because ",
                        "they link directly to ECF grading codes and ",
                        "probably link other records for these players to ",
                        "their ECF grading code.",
                    )
                ),
                "\n".join(linkers),
            )

        # Do the updates.
        # Note that games are the only records that need creating at this
        # stage. The other records (names players and events) had to be
        # created earlier so they could be referenced. It is not possible
        # to delete event records as part of this process because the
        # document driving the update does not contain the names of sections
        # to be replaced. Some section deletions are deduced: new document
        # for EventA with sections Open and Major will cause deletion of
        # section Minor if database holds EventA with sections Open and
        # Minor because the match on Open causes an amend to happen rather
        # than an insert.
        for og, ng in zip(dbgames, newgames):
            ng.key.recno = og.key.recno
            og.edit_record(
                self._database,
                filespec.GAME_FILE_DEF,
                filespec.GAME_FIELD_DEF,
                ng,
            )
        # pycodestyle E203 whitespace before ':'.
        # black formatting insists on the space.
        for og in dbgames[len(newgames) :]:
            og.delete_record(self._database, filespec.GAME_FILE_DEF)
        # pycodestyle E203 whitespace before ':'.
        # black formatting insists on the space.
        for ng in newgames[len(dbgames) :]:
            ng.put_record(self._database, filespec.GAME_FILE_DEF)
        namemanager.update_names()
        for key, value in players.items():
            if not playersgames[key]:
                value.delete_record(self._database, filespec.PLAYER_FILE_DEF)
            elif key in playersamend:
                value.edit_record(
                    self._database,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                    playersamend[key],
                )
        for key, value in merges.items():
            value.edit_record(
                self._database,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
                mergesamend[key],
            )
        for key, value in eventsamend.items():
            eventskey[key].edit_record(
                self._database,
                filespec.EVENT_FILE_DEF,
                filespec.EVENT_FIELD_DEF,
                value,
            )
        for item in dbevents:
            record = item[2]
            record.delete_record(self._database, filespec.EVENT_FILE_DEF)


class NameManager:
    """Manage name lookup and reference counts for a collation.

    Originally local attributes of update_players but merge_players needs this
    stuff when handling take-on of results from ECF submission files and League
    program database dumps.

    """

    def __init__(self, database):
        """Initialise name lookup data structures."""
        super().__init__()
        self._database = database
        # These were local attributes of CollationDB.update_results originally.
        self.names = {}  # {name : ResultsDBrecordName instance, ...}
        self.namesamend = {}  # {name : names[name].clone(), ...}
        self.nameskey = {}  # {srkey : name, ...}
        self.namesmap = {}  # {name : srkey, ...}

    def set_name(self, name):
        """Create name record adjust reference count and return key."""
        if name not in self.names:
            nrdb = self._database.get_primary_record(
                filespec.NAME_FILE_DEF,
                self._database.database_cursor(
                    filespec.NAME_FILE_DEF, filespec.NAMETEXT_FIELD_DEF
                ).get_unique_primary_for_index_key(
                    self._database.encode_record_selector(name)
                ),
            )
            if nrdb is not None:
                nrdb = get_name_from_record_value(nrdb)
            if nrdb is None:
                nr = ResultsDBrecordName()
                nr.value.name = name
                nr.value.reference_count = 1
                nr.key.recno = None
                nr.put_record(self._database, filespec.NAME_FILE_DEF)
                self.names[name] = nr
                self.namesmap[name] = nr.key.recno
                self.nameskey[nr.key.recno] = name
                return self.namesmap[name]
            self.names[name] = nrdb
            self.namesmap[name] = nrdb.key.recno
            self.nameskey[nrdb.key.recno] = name
        if name not in self.namesamend:
            self.namesamend[name] = self.names[name].clone()
            self.namesamend[name].value.reference_count += 1
        else:
            self.namesamend[name].value.reference_count += 1
        return self.namesmap[name]

    def unset_name(self, skey):
        """Adjust reference count for name key and return name."""
        if skey not in self.nameskey:
            nr = get_name_from_record_value(
                self._database.get_primary_record(filespec.NAME_FILE_DEF, skey)
            )
            self.nameskey[skey] = nr.value.name
            name = self.nameskey[skey]
            self.namesmap[name] = skey
            self.names[name] = nr
            self.namesamend[name] = self.names[name].clone()
        else:
            name = self.nameskey[skey]
        self.namesamend[name].value.reference_count -= 1
        return name

    def update_names(self):
        """Apply the collected updates to names."""
        for key, value in self.names.items():
            if key in self.namesamend:
                count = self.namesamend[key].value.reference_count
                if count <= 0:
                    value.delete_record(self._database, filespec.NAME_FILE_DEF)
                elif value.value.reference_count != count:
                    value.edit_record(
                        self._database,
                        filespec.NAME_FILE_DEF,
                        filespec.NAME_FIELD_DEF,
                        self.namesamend[key],
                    )

    def get_code(self, name):
        """Return the code for the name from name:code map."""
        return self.namesmap[name]

    def get_code_default(self, name, default=None):
        """Return the code for the name from name:code map or the default."""
        return self.namesmap.get(name, default)
