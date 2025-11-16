# type: ignore

from fastapi import APIRouter, WebSocket
import json

from classes.game import Game, games, GameState

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/create_game")
def create_game():
    new_game = Game()
    games[new_game.code] = new_game
    return {"code": new_game.code}


@router.websocket("/{game_code}")
async def websocket_endpoint(websocket: WebSocket, game_code: str):
    # First, check if the game even exists
    if game_code not in games:
        # Close the connection immediately if the game ID is invalid
        await websocket.close(code=1008)  # 1008 = Policy Violation
        return

    # If the game exists, get it
    game = games[game_code]

    # Next, check if the game is full
    if game.plr_count >= 2:
        # Close the connection if the game is full
        await websocket.close(code=1013)  # 1013 = Try Again Later (or 1000)
        return

    # If the game exists AND is not full, accept the connection
    await websocket.accept()
    # You must 'await' sending messages
    await websocket.send_text(f"Joined game with code: {game_code}")

    if game.lobby is not None:
        game.lobby.unassigned.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # treat empty or invalid JSON as a request for current game state
            data_dict = {}
            action = ""
            try:
                if data and data.strip():
                    data_dict = json.loads(data)
                    action = data_dict.get("action", "")
            except Exception:
                data_dict = {}
                action = ""

            send = {}
            if data_dict and "action" in data_dict:
                action = data_dict["action"]

            # if the client sent an empty request (common after receiving a broadcast),
            # reply with the game_data for this websocket when the game is active.
            if not data_dict:
                if game.state == GameState.Active:
                    player = game.get_player_by_socket(websocket)
                    send_data = {"game": game.serialize(), "player": player.serialize()}
                    send["game_data"] = send_data
                    await websocket.send_text(json.dumps(send))
                    continue
                else:
                    send["game_data"] = {"game": game.serialize()}
                    await websocket.send_text(json.dumps(send))
                    continue

            if game.state == GameState.Lobby:
                if action == "join":
                    print("joining")
                    team = data_dict["team"]
                    print(team)
                    game.lobby.change_team(websocket, team.upper() == "IRT")
                    game.plr_count = len(
                        [p for p in (game.lobby.irt, game.lobby.bmt) if p is not None]
                    )

                if action == "start":
                    print("attempting start")
                    print(
                        game.lobby.unassigned,
                        game.lobby.irt,
                        game.lobby.bmt,
                        game.lobby.can_start(),
                    )
                    if game.lobby.can_start():
                        print("starting!")
                        await game.start_game()
                        await game.broadcast(json.dumps({"action": "start"}))
                        # don't fall through to the per-connection send below
                        continue

            if game.state == GameState.Active:
                player = game.get_player_by_socket(websocket)
                await websocket.send_text(f"Message text was: {data}")

                if action == "bid":
                    # modify to be able to use any object
                    bid = data_dict["bid"]
                    obj = data_dict["biddable"]
                    await game.get_contract_by_object(obj).add_bid(player, bid)

                if action == "build":
                    line = data_dict["line"]
                    id = data_dict["id"]
                    await game.get_line_by_name(line).build_station(id)

                if action == "end_turn":
                    player.end_turn = True
                    await game.next_year()

                send_data = {"game": game.serialize(), "player": player.serialize()}

                send["game_data"] = send_data
            await websocket.send_text(json.dumps(send))

    except Exception as e:
        # This block will run if the client disconnects or an error occurs
        print(f"WebSocket error or client disconnected: {e}")
    finally:
        # 'finally' ensures this code runs no matter what,
        # cleaning up the connection when the 'try' block exits.
        await websocket.close()
        # recompute player count after disconnect
        if hasattr(game, "lobby") and game.lobby is not None:
            game.plr_count = len(
                [p for p in (game.lobby.irt, game.lobby.bmt) if p is not None]
            )
