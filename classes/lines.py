import json
import random
import re
import select
from typing_extensions import Dict
from pathlib import Path
from classes.player import Player


class Station:
    def __init__(self, name: str):
        self.owner: Player | None = None
        self.built = False
        self.price = round(random.uniform(1, 10),1)
        self.profit = round(random.uniform(1,4),1)
        self.name = name
        self.year = 0

    def addOwner(self, owner):
        self.owner = owner

    def build(self):
        if self.owner is None:
            raise ValueError("Station has no owner")
        self.owner.money -= self.cost
        self.built = True
    
    def serialize(self):
        return {
            "name": self.name,
            "owner": self.owner.name,
            "built": self.built,
            "cost": self.cost,
            "profit": self.profit,
            "year": self.year
        }



class Line:
    def __init__(self, name: str):
        self.name = name
        self.stations:Dict[str, Station] = dict()
        self.owner: Player | None = None
        self.price = 0
        self.bought = False
        self.active = False

    def serialize(self):
        return {
            "name": self.name,
            "stations" : self.stations,
            "owner": self.owner,
            "price": self.price,
            "bought": self.bought,
            "active": self.active,

        }

    def bidLine(self, bidder, bid_amount):
        if bid_amount > self.price - 0.:
            raise ValueError(
                f"Bid amount {bid_amount} is less than the current price {self.price} for line {self.name}")
        self.owner = bidder
        self.price = bid_amount

    def calculateProfit(self):
        total_profit = {"IRT": 0, "BMT": 0, "IND": 0}
        built = [station for station in self.stations.values() if station.built]
        if len(built) == 0:
            return 0

        for station in built:
            owner_name = station.owner.name if station.owner is not None else None
            if owner_name in total_profit:
                total_profit[owner_name] += station.profit

        if len(built) == len(self.stations):
            owners = {s.owner.name for s in built if s.owner is not None}
            if len(owners) == 1:
                owner = next(iter(owners))
                total_profit[owner] = int(total_profit[owner] * 1.2)

        return total_profit


    def changeOwner(self, new_owner):
        self.owner = new_owner

    def buildStation(self, station_name: str, owner):
        if owner != self.owner:
            raise ValueError(
                f"Owner {owner} does not have permission to build station on line {self.name}"
            )
        if station_name in self.stations:
            station = self.stations[station_name]
            station.build()
        else:
            raise ValueError(f"Station {station_name} does not exist")
            # print(f"Station {station_name} does not exist")


lines: Dict[str, Line] = {}

data_path = Path(__file__).parent / "lines.json"
if data_path.exists():
    with data_path.open("r") as f:
        data = json.load(f)
        for line in data.get("lines", []):
            new_line = Line(line["name"])
            new_line.price = line.get("price", 0)
            for station_name in line.get("stations", []):
                new_line.stations[station_name] = Station(station_name)
            lines[line["name"]] = new_line

print(f"Loaded {len(lines)} lines from lines.json")
