# from asyncio.unix_events import SelectorEventLoop
from fastapi import WebSocket


class Player:
    def __init__(self, name: str):
        self.name = name
        self.money = 0  # change to some inital
        self.money_bidded = 0
        self.WebSocket: WebSocket | None = None
        self.end_turn: bool = False

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "money": self.money,
        }

    # def addLine(self, line):
    #     if self.money < line.price:
    #         print("not enough money")
    #         return
    #     self.money -= line.price
    #     self.lines.append(line.name)
    #     line.bought = True

    # if line.owner != None:
    #     if higerbid():
    #         pass

    # pass
