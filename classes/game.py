import enum
import json
import uuid
from fastapi import WebSocket
from typing_extensions import Dict, List

from classes.contract import Contract
from classes.line import Line, lines
from classes.lobby import Lobby
from classes.player import Player
from classes.station import Station


class GameState(enum.Enum):
    Lobby = 1
    Active = 2
    Finished = 3


class Game:
    def __init__(self):
        self.state: GameState = GameState.Lobby
        self.lobby: Lobby | None = Lobby()
        self.players = {
            "IRT": Player("IRT"),
            "IND": Player("IND"),
            "BMT": Player("BMT"),
        }
        self.plr_count = 0

        self.code = str(uuid.uuid4())[:8]
        self.year: int = 1879
        self.turn: int = 0
        self.lines: List[Line] = lines.copy()
        self.contracts: List[Contract] = []

    def serialize(self) -> dict[str, object]:
        return {
            "code": self.code,
            "year": self.year,
            "turn": self.turn,
            "lines": [
                line.serialize()
                for line in self.lines
                if line.year <= (self.turn + 1) * 10 + 1880
            ],
            "contracts": [contract.serialize() for contract in self.contracts],
        }

    def get_contract_by_object(self, obj: str) -> Contract:
        return next(
            (contract for contract in self.contracts if contract.biddable.isObj(obj))
        )

    async def start_game(self):
        if self.lobby is not None:
            self.players["IRT"].WebSocket = self.lobby.irt
            self.players["BMT"].WebSocket = self.lobby.bmt

        # IMPLEMENT STARTER LINES
        await self.next_year()

        self.lobby = None
        self.state = GameState.Active

    async def end_game(self):
        win = {"action": "win", "team": "tie"}
        if self.players["IRT"].money > self.players["BMT"].money:
            win["team"] = "IRT"
        elif self.players["IRT"].money < self.players["BMT"].money:
            win["team"] = "BMT"
        await self.broadcast(json.dumps(win))

        if self.players["IRT"].WebSocket is not None:
            await self.players["IRT"].WebSocket.close()
        if self.players["BMT"].WebSocket is not None:
            await self.players["BMT"].WebSocket.close()

        self.players["IRT"].WebSocket = None
        self.players["BMT"].WebSocket = None

        del games[self.code]

    async def broadcast(self, message: str) -> None:
        for player in self.players.values():
            if player.WebSocket is not None:
                await player.WebSocket.send_text(message)

    def get_player_by_name(self, name: str) -> Player:
        name = name.upper()

        if name not in self.players:
            raise ValueError(f"Player {name} does not exist in this game")

        return self.players[name]

    def get_line_by_name(self, name: str) -> Line:
        return next(line for line in self.lines if line.name == name)

    def get_player_by_socket(self, websocket: WebSocket) -> Player:
        for player in self.players.values():
            if player.WebSocket == websocket:
                return player

        raise ValueError("No player found for the given WebSocket")

    async def next_year(self) -> None:
        for player in self.players.values():
            if player.WebSocket is not None and not player.end_turn:
                return

        # Checks for awareded lines that the owner did not build 2 stations in after the 2 year grace period
        for line in self.lines:
            if (
                (line.awarded_year + 2 < self.year)
                and (line.count_built_stations() < 2)
                and (line.owner is not None)
            ):
                contract: Contract = Contract(
                    biddable=line,
                    year=self.year,
                )

                self.contracts.append(contract)

        # Collect revenue
        for line in self.lines:
            line.collect_revenue()

        # Award contracts and remove them
        for contract in self.contracts:
            if contract.deadline_year == self.year:
                contract.award_contract()
        self.contracts = [
            contract
            for contract in self.contracts
            if contract.deadline_year > self.year
        ]

        self.year += 1

        if self.year % 10 == 0:
            await self.next_turn()

        for player in self.players.values():
            player.end_turn = False

        for player in self.players.values():
            if player.WebSocket is not None:
                await player.broadcast(
                    json.dumps(
                        {
                            "game_data": {
                                "game": self.serialize(),
                                "player": player.serialize(),
                            }
                        }
                    )
                )

    async def next_turn(self) -> None:
        self.turn += 1

        if self.turn > 7:
            await self.end_game()

        if self.turn <= 4:
            for line in self.lines:
                if (
                    line.year < (self.turn + 1 * 10) + 1880
                    and line.year < (self.turn * 10) + 1880
                ):
                    contract: Contract = Contract(
                        biddable=line,
                        year=self.year,
                    )
                    self.contracts.append(contract)
        else:
            for line in self.lines:
                if (
                    line.year < (self.turn + 1 * 10) + 1880
                    and line.year < (self.turn * 10) + 1880
                ):
                    for station in line.stations.values():
                        if station.owner is None:
                            contract = Contract(
                                biddable=station,
                                year=self.year,
                            )
                            self.contracts.append(contract)

    # def get_player_stations(self, player: Player) -> list[Station]:
    #     active_lines = (ln for ln in lines.values() if ln.active)
    #     ret = []
    #     for line in active_lines:
    #         for station in line.stations.values():
    #             if station.owner is player:
    #                 ret.append(station)
    #     return ret


games: Dict[str, Game] = {}
