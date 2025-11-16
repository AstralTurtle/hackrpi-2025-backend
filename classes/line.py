from pathlib import Path
from typing_extensions import Dict

from classes.player import Player
from classes.station import Station

import json


class Line:
    def __init__(self, name: str, year: int, stations: list[str]):
        self.name = name
        self.year = year
        self.stations: Dict[str, Station] = dict()
        for id in stations:
            self.stations[id] = Station(id)

        self.owner: Player | None = None
        self.awarded_year = 0

    def serialize(
        self,
    ):
        return {
            "name": self.name,
            "year": self.year,
            "stations": [station.serialize() for station in self.stations.values()],
            "owner": self.owner,
        }

    def set_owner(self, new_owner: Player | None):
        self.owner = new_owner
        for station in self.stations.values():
            station.set_owner(new_owner)

    def isObj(self, obj: str):
        return obj == self.name

    def count_built_stations(self) -> int:
        built_count = 0
        for station in self.stations.values():
            if station.built:
                built_count += 1

        return built_count

    def is_fully_owned(self) -> bool:
        for station in self.stations.values():
            if station.owner != self.owner:
                return False

        return True

    async def build_station(self, id: str):
        await self.stations[id].build()

    def collect_revenue(self):
        all_revenue: dict[Player, float] = dict()
        for station in self.stations.values():
            if station.owner is not None:
                all_revenue[station.owner] += station.revenue

        if self.is_fully_owned() and self.owner is not None:
            all_revenue[self.owner] = float(all_revenue[self.owner] * 1.2)

        if self.count_built_stations() < 2:
            return

        for owner, revenue in all_revenue.items():
            owner.money += revenue


lines: list[Line] = []

root = Path(__file__).resolve().parent.parent

data = root / "data" / "lines.json"

with data.open(encoding="utf-8") as d:
    lines_data = json.load(d)

    for line in lines_data["lines"]:
        new_line = Line(line["name"], line["year"], line["stations"])
        lines.append(new_line)
