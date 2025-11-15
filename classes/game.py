import enum
import uuid

from fastapi import WebSocket
from typing_extensions import Dict

from classes.lines import lines
from classes.lobby import Lobby
from classes.player import Player



class GameState(enum.Enum):
    Lobby = 1
    Active = 2
    Finished = 3

class Game:
    def __init__(self):
        uuid_str = str(uuid.uuid4())
        self.code = uuid_str[:8]
        self.plr_count = 0
        self.players = {
            "IRT": Player("IRT"),
            "IND": Player("IND"),
            "BMT": Player("BMT"),
        }
        self.year: int = 1940
        self.turn: int = 0
        self.state: GameState = GameState.Lobby
        self.lobby: Lobby = Lobby()

    def start_game(self):
        self.state = GameState.Active
        self.players["IRT"].WebSocket = self.lobby.irt
        self.players["BMT"].WebSocket = self.lobby.bmt
        self.lobby = None
        self.state = GameState.Active

    def serialize(self):
        return {
            "code": self.code,
            "year": self.year,
            "turn": self.turn,
        }

    def get_player(self, player: str) -> Player:
        company = player.upper()

        if company not in self.players:
            raise ValueError(f"Player {company} does not exist in this game")

        return self.players[company]

    def get_player_by_socket(self, websocket) -> Player:
        for player in self.players.values():
            if player.WebSocket == websocket:
                return player

        raise ValueError("No player found for the given WebSocket")

    # add new contracts and game rules
    def nextTurn(self) -> None:
        """Advance the game turn and apply turn-specific rules."""
        self.turn += 1

        if self.turn == 1:
            # rules for turn 1
            pass
        elif self.turn == 2:
            # rules for turn 2
            pass
        elif self.turn == 3:
            # rules for turn 3
            pass
        else:
            # default behavior for unexpected turn values
            pass

    # calculate profits and finish bids
    def nextYear(self) -> None:
        active_lines = (ln for ln in lines.values() if ln.active)

        for line in active_lines:
            if not line.bought and line.owner is not None:
                line.owner.addLine(line)

        for player in self.players.values():
            total_profit = 0
            for line in player.lines:
                total_profit += line.calculateProfit()
            player.money += total_profit

        self.year += 1

        if self.year % 10 == 0:
            self.nextTurn()


games: Dict[str, Game] = {}
