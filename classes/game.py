import enum
import json
import uuid

from typing_extensions import Dict

from classes.lines import Station, lines
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
        self.year: int = 1880
        self.turn: int = 0
        self.state: GameState = GameState.Lobby
        self.lobby: Lobby = Lobby()
        self.lines = []
        self.contracts = []

    def start_game(self):
        self.state = GameState.Active
        self.players["IRT"].WebSocket = self.lobby.irt
        self.players["BMT"].WebSocket = self.lobby.bmt
        # initalize lines

        self.lobby = None
        self.state = GameState.Active

    async def end_game(self):
        win = {"action": "win", "team": "tie"}
        if self.players["IRT"].money > self.players["BMT"].money:
            win["team"] = "IRT"
        elif self.players["IRT"].money < self.players["BMT"].money:
            win["team"] = "BMT"
        await self.broadcast(json.dumps(win))

        self.players["IRT"].WebSocket.close()
        self.players["BMT"].WebSocket.close()
        self.players["IRT"].WebSocket = None
        self.players["BMT"].WebSocket = None

        del games[self.code]

    def serialize(self):
        return {
            "code": self.code,
            "year": self.year,
            "turn": self.turn,
            "contracts": self.contracts,
            "lines": self.lines,
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

    # add new contracts and game rules, moves to next decade
    def nextTurn(self) -> None:
        """Advance the game turn and apply turn-specific rules."""
        self.turn += 1
        if self.turn > 7:
            self.end_game()
        if self.turn < 3:  # before 4th
            for line in self.lines:
                if (
                    line.year > (self.turn + 1 * 10) + 1880
                    and line.year > (self.turn * 10) + 1880
                ):
                    lines += line
                    self.contracts += line
        else:  # after 4th
            for line in self.lines:
                if (
                    line.year > (self.turn + 1 * 10) + 1880
                    and line.year > (self.turn * 10) + 1880
                ):
                    lines += line
                    for station in line.stations.value():
                        self.contracts += station

    def bid(obj, bidder, bid_amount):
        if bid_amount < obj.price:
            raise ValueError(
                f"Bid amount {bid_amount} is less than the current price {obj.price} for line {obj.name}"
            )
        obj.owner = bidder
        obj.price = bid_amount

    # calculate profits and finish bids
    def nextYear(self) -> None:
        for player in self.players.values():
            if player.WebSocket is not None and not player.end_turn:
                return

        active_lines = (ln for ln in lines.values() if ln.active)

        total_profit = {"IRT": 0, "BMT": 0, "IND": 0}
        for line in active_lines:
            tp = line.calculateProfit()
            for k, v in tp.items():
                total_profit[k] += v

        for k, v in total_profit.items():
            self.players[k].money += v

        self.year += 1

        if self.year % 10 == 0:
            self.nextTurn()

        for player in self.players.values():
            player.end_turn = False

    # unused???
    def get_player_stations(self, player: Player) -> list[Station]:
        active_lines = (ln for ln in lines.values() if ln.active)
        ret = []
        for line in active_lines:
            for station in line.stations.values():
                if station.owner is player:
                    ret.append(station)
        return ret

    async def broadcast(self, message: str) -> None:
        for player in self.players.values():
            if player.WebSocket is not None:
                await player.WebSocket.send_text(message)


games: Dict[str, Game] = {}
