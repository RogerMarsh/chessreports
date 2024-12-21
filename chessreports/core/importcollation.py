# importcollation.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Collate results imported from another results database."""

from chessvalidate.core import gameobjects

from . import constants
from .importreports import get_player_identifier

homeplayercolour = {"yes": True, "no": False}


class ImportCollation(gameobjects.GameCollation):
    """Results extracted from an export file from a results database."""

    def __init__(self, importreport):
        """Extend, collate results from a results database export file.

        importreport - an importreports.ImportReports instance

        """
        super().__init__()

        # Restore error attribute removed from GameCollation because main
        # subclass does not want it now.
        # round=game.get(constants.ROUND_LOWER) is ok, compared with SwissGame,
        # because ImportReports class sets the game value to a str if at all.
        self.error = []

        self.importreport = importreport
        for game in importreport.game.values():
            if (
                constants.HOMETEAM not in game
                or constants.AWAYTEAM not in game
            ):
                sectionkey = game[constants.SECTION]
                section = self.games.setdefault(
                    sectionkey,
                    gameobjects.Section(
                        competition=game[constants.SECTION], games=[]
                    ),
                )
            else:
                sectionkey = (
                    game[constants.SECTION],
                    (
                        game[constants.HOMETEAM],
                        game[constants.AWAYTEAM],
                        " ".join(
                            (
                                game[constants.SECTION],
                                game[constants.DATE],
                            )
                        ),
                    ),
                )
                section = self.games.setdefault(
                    sectionkey,
                    gameobjects.MatchReport(
                        competition=game[constants.SECTION],
                        hometeam=game[constants.HOMETEAM],
                        awayteam=game[constants.AWAYTEAM],
                        round=game.get(constants.ROUND_LOWER),
                        games=[],
                    ),
                )
            # pylint W0632 unbalanced-tuple-unpacking.
            # self.collate_game_players returns a list with two items.
            hp, ap = self.collate_game_players(game)
            hpw = homeplayercolour.get(game.get(constants.HOMEPLAYERWHITE))
            if constants.ROUND_LOWER in game:
                if constants.BOARD_LOWER in game:
                    section.games.append(
                        gameobjects.SwissMatchGame(
                            round=game[constants.ROUND_LOWER],
                            board=game[constants.BOARD_LOWER],
                            result=game[constants.RESULT],
                            date=game[constants.DATE],
                            homeplayerwhite=hpw,
                            homeplayer=hp,
                            awayplayer=ap,
                        )
                    )
                else:
                    section.games.append(
                        gameobjects.SwissGame(
                            round=game[constants.ROUND_LOWER],
                            result=game[constants.RESULT],
                            date=game[constants.DATE],
                            homeplayerwhite=hpw,
                            homeplayer=hp,
                            awayplayer=ap,
                        )
                    )
            elif constants.BOARD_LOWER in game:
                section.games.append(
                    gameobjects.MatchGame(
                        board=game[constants.BOARD_LOWER],
                        result=game[constants.RESULT],
                        date=game[constants.DATE],
                        homeplayerwhite=hpw,
                        homeplayer=hp,
                        awayplayer=ap,
                    )
                )
            else:
                section.games.append(
                    gameobjects.Game(
                        result=game[constants.RESULT],
                        date=game[constants.DATE],
                        homeplayerwhite=hpw,
                        homeplayer=hp,
                        awayplayer=ap,
                    )
                )

    def collate_game_players(self, game):
        """Return list of gameobjects.Player for players in game."""
        pl = []
        for player, pin, affiliation, team, reportedcodes in (
            (
                constants.HOMENAME,
                constants.HOMEPIN,
                constants.HOMEAFFILIATION,
                constants.HOMETEAM,
                constants.HOMEREPORTEDCODES,
            ),
            (
                constants.AWAYNAME,
                constants.AWAYPIN,
                constants.AWAYAFFILIATION,
                constants.AWAYTEAM,
                constants.AWAYREPORTEDCODES,
            ),
        ):
            pk = get_player_identifier(game, player, pin, affiliation)
            p = self.players.get(pk)
            if p is None:
                if game[team] is not None:
                    section = None
                else:
                    section = game[constants.SECTION]
                attr = {
                    "name": pk[0],
                    "event": pk[1],
                    "startdate": pk[2],
                    "enddate": pk[3],
                    "section": section,
                    "pin": pk[5],
                    "reported_codes": game[reportedcodes],
                }
                if game[team]:
                    p = gameobjects.Player(club=pk[4], **attr)
                else:
                    p = gameobjects.Player(**attr)
                if constants.BOARD_LOWER in game:
                    p.affiliation = game[affiliation]
                self.players[pk] = p
            pl.append(p)
        return pl
