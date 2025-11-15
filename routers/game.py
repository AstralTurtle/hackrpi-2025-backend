from fastapi import APIRouter, WebSocket
import json
from classes.game import Game, games, GameState
from classes.lobby import Lobby
from classes.lines import lines, Line

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/create_game")
def create_game():
	new_game = Game()
	games[new_game.code] = new_game


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

	

	try:
		while True:
			
			data = await websocket.receive_text()
			dict = json.loads(data)
			send = {}
			action = ""
			if dict.has("action"):
				action = dict[action]
			if game.state == GameState.Lobby:
				if action == "join":
					team = dict["team"]
					game.lobby.change_team(websocket, team.upper() == "IRT")

				if action == "start" and game.lobby.can_start():
					game.start_game()





			if game.state == GameState.Active:
				player = game.get_player_by_socket(websocket)
				await websocket.send_text(f"Message text was: {data}")

				if action == "bid":
					line = dict["line"]
					lines[line].bidLine(player, dict["amount"])

				if action == "build":
					line = dict["line"]
					lines[line].buildStation(dict["station"], player)


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
		game.plr_count -=1 
