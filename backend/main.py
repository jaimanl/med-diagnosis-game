from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
import uuid

# Load .env variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS for dev/Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Vercel frontend origin later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store
active_games = {}

@app.get("/")
def root():
    return {"message": "Backend is live!"}


@app.websocket("/ws/{game_id}/{player_name}")
async def game_ws(websocket: WebSocket, game_id: str, player_name: str):
    await websocket.accept()

    if game_id not in active_games:
        # Create new game and AI-generated case
        case_text, correct_dx = await generate_case()
        active_games[game_id] = {
            "players": {},
            "case": case_text,
            "answer": correct_dx,
            "round_active": True,
        }

    game = active_games[game_id]
    game["players"][player_name] = websocket

    # Send intro message to the player
    await websocket.send_text(f"🩺 Case: {game['case']}")

    try:
        while True:
            msg = await websocket.receive_text()

            # Interpret message (basic protocol)
            if msg.lower().startswith("guess:"):
                diagnosis = msg.split("guess:", 1)[1].strip().lower()
                if diagnosis == game["answer"].lower() and game["round_active"]:
                    game["round_active"] = False
                    # Notify all players who got it
                    for name, ws in game["players"].items():
                        await ws.send_text(
                            f"✅ {player_name} correctly diagnosed: {game['answer']}"
                        )
                else:
                    await websocket.send_text("❌ Incorrect diagnosis. -1 point.")
            elif msg.lower().startswith("ask:"):
                question = msg.split("ask:", 1)[1].strip()
                answer = await respond_to_question(game["case"], question)
                await websocket.send_text(f"📋 Response: {answer}")
            else:
                await websocket.send_text("⚠️ Unknown command. Use 'ask:' or 'guess:'")

    except WebSocketDisconnect:
        del game["players"][player_name]


# 🧠 Use GPT to generate a case
async def generate_case():
    prompt = (
        "Create a medium-difficulty medical mystery case (5-question limit). "
        "Describe only the presenting symptoms, physical findings, and vitals. "
        "Also provide the correct diagnosis, clearly labeled."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    text = response.choices[0].message.content
    if "Diagnosis:" in text:
        case, answer = text.split("Diagnosis:", 1)
    else:
        case, answer = text, "unknown"

    return case.strip(), answer.strip()


# 🩺 Use GPT to answer clinical questions
async def respond_to_question(case_context, question):
    prompt = (
        f"A student is investigating this case:\n\n{case_context}\n\n"
        f"The student asks: {question}\n\nRespond concisely as a teaching assistant."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
