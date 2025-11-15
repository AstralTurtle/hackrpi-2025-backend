# from asyncio.unix_events import SelectorEventLoop
from fastapi import WebSocket



class Player:
    def __init__(self, name: str):
        self.name = name
        self.money = 0  # change to some inital
        self.money_bidded = 0
        self.lines = []
        self.WebSocket: WebSocket | None = None

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "money": self.money,
            "lines": [line.name for line in self.lines],
        }


    def addLine(self, line):
        if self.money < line.price:
            print("not enough money")
            return
        self.money -= line.price
        self.lines.append(line)
        line.bought = True

        # if line.owner != None:
        #     if higerbid():
        #         pass

        pass
