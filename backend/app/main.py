from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from app.scraper import fetch_article_text
from app.script_gen import generate_dialogue
from app.tts import render_dialogue_to_audio

app = FastAPI(title="Narrated")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class NarrateRequest(BaseModel):
    url: str


@app.post("/api/narrate")
def narrate(req: NarrateRequest):
    try:
        article_text = fetch_article_text(req.url)
        dialogue = generate_dialogue(article_text)
        audio_bytes = render_dialogue_to_audio(dialogue)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Narration failed: {e}")

    return Response(content=audio_bytes, media_type="audio/mpeg")


@app.get("/api/health")
def health():
    return {"status": "ok"}
