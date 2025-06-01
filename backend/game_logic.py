
import uuid

def create_new_game():
    return {
        "id": str(uuid.uuid4()),
        "players": {},
        "case": None,
        "answer": None,
        "round_active": True,
    }

def add_player(game, player_name, websocket):
    game["players"][player_name] = websocket

def is_correct_guess(game, guess):
    return guess.strip().lower() == game["answer"].strip().lower()

def end_round(game):
    game["round_active"] = False

def reset_game(game):
    game["case"] = None
    game["answer"] = None
    game["round_active"] = True
