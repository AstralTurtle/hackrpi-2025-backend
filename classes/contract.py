import json
from classes.line import Line
from classes.player import Player
from classes.station import Station


class Contract:
    def __init__(self, biddable: Line | Station, year: int):
        self.biddable: Line | Station = biddable
        self.highest_bid: int = 0
        self.type = "line" if isinstance(biddable, Line) else "station"
        self.highest_bidder: Player | None = None
        self.deadline_year: int = year + 2

    def serialize(self):
        return {
            "biddable": self.biddable.serialize(),
            "highest_bid": self.highest_bid,
            "highest_bidder": self.highest_bidder.serialize()
            if self.highest_bidder is not None
            else None,
            "deadline_year": self.deadline_year,
            "type": self.type,
        }

    async def add_bid(self, bidder: Player, amount: int):
        if amount > bidder.money:
            await bidder.broadcast(
                json.dumps({"notify": "You do not have enough money to bid."})
            )
            return

        if amount > self.highest_bid:
            self.highest_bid = amount
            self.highest_bidder = bidder

    def award_contract(self):
        if self.highest_bidder is not None:
            self.highest_bidder.money -= self.highest_bid
            self.biddable.set_owner(self.highest_bidder)
