from fastapi import WebSocket


class Lobby:
    def __init__(self):
        self.unassigned: list[WebSocket] = []
        self.irt: WebSocket | None = None
        self.bmt: WebSocket | None = None

    def change_team(self, player: WebSocket, joinIRT: bool):
        if self.irt is None and joinIRT:
            if player in self.unassigned:
                self.unassigned.remove(player)
                self.irt = player
            elif player is self.bmt:
                self.bmt = None
                self.irt = player
        elif self.bmt is None and not joinIRT:
            if player in self.unassigned:
                self.unassigned.remove(player)
                self.bmt = player
            elif player is self.irt:
                self.irt = None
                self.bmt = player

    def can_start(self):
        return self.irt is not None and self.bmt is not None
