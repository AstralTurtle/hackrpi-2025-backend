# from asyncio.unix_events import SelectorEventLoop
from fastapi import WebSocket

INITIAL_MONEY: float = 1000


class Player:
    def __init__(self, name: str):
        self.name = name
        self.money = INITIAL_MONEY

        self.end_turn: bool = False

        self.WebSocket: WebSocket | None = None

    def serialize(self) -> dict[str, str | float]:
        return {
            "name": self.name,
            "money": self.money,
        }

    async def broadcast(self, message: str):
        if self.WebSocket is None:
            return

        await self.WebSocket.send_text(message)
