import random

from classes.player import Player
import json


class Station:
    def __init__(self, id: str):
        self.id = id

        self.owner: Player | None = None
        self.awarded_year = 0
        self.built = False
        self.cost = round(random.uniform(1, 10), 1)
        self.revenue = round(random.uniform(1, 4), 1)

    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.serialize() if self.owner is not None else None,
            "awarded_year": self.awarded_year,
            "built": self.built,
            "cost": self.cost,
            "revenue": self.revenue,
        }

    def set_owner(self, new_owner: Player | None):
        self.owner = new_owner

    def isObj(self, obj: str):
        return obj == self.id

    async def build(self):
        if self.owner is None or self.built:
            return
            # ValueError("Station has no owner")

        if self.owner.money < self.cost:
            await self.owner.broadcast(
                json.dumps(
                    {"notify": "You do not have enough money to build this station."}
                )
            )

        self.owner.money -= self.cost
        self.built = True
