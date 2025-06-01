from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS config for local dev + Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, use wildcard — lock down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is live!"}

@app.websocket("/ws/{game_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_name: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from {player_name}: {data}")
            # For now, just echo back
            await websocket.send_text(f"You said: {data}")
    except WebSocketDisconnect:
        print(f"{player_name} disconnected")

# (Optional) You could also add routes to generate cases from OpenAI, store moves, etc.
