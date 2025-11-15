import json
from random import randint
from typing_extensions import Dict

import os
from classes.player import Player


class Station:
    def __init__(self, name: str):
        self.owner: Player | None = None
        self.built = False
        self.cost = randint(100, 500)
        self.profit = randint(50, 150)
        self.name = name

    def addOwner(self, owner):
        self.owner = owner

    def build(self):
        if self.owner is None:
            raise ValueError("Station has no owner")
        self.owner.money -= self.cost
        self.built = True



class Line:
    def __init__(self, name: str):
        self.name = name
        self.stations:Dict[str, Station] = dict()
        self.owner: Player | None = None
        self.price = 0
        self.bought = False
        self.active = False

    def bidLine(self, bidder, bid_amount):
        if bid_amount < self.price:
            raise ValueError(
                f"Bid amount {bid_amount} is less than the current price {self.price} for line {self.name}")
        self.owner = bidder
        self.price = bid_amount

    def calculateProfit(self):
        total_profit = 0
        built = [station for station in self.stations.values() if station.built]
        for station in built:
            total_profit += station.profit

        if len(built) == len(self.station.values()): total_profit = int(total_profit * 1.2)  # 20% bonus for all stations built

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


# # Get the full path of the current working directory
# current_directory_path = os.getcwd()

# # Extract the directory name from the full path
# current_directory_name = os.path.basename(current_directory_path)


# with open(f"{}lines.json", "r") as f:
#     data = json.load(f)
#     for line in data.get("lines", []):
#         new_line = Line(line["name"])
#         new_line.price = line.get("price", 0)
#         for station_name in line.get("stations", []):
#             new_line.stations[station_name] = Station(station_name)
#         lines[line["name"]] = new_line

# print(f"Loaded {len(lines)} lines from lines.json")
