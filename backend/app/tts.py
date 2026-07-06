import io
import os

from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

VOICE_IDS = {
    "alex": os.environ.get("ELEVENLABS_VOICE_ALEX", "21m00Tcm4TlvDq8ikWAM"),
    "sam": os.environ.get("ELEVENLABS_VOICE_SAM", "AZnzlk1XvdvUeBnXmlld"),
}


def render_dialogue_to_audio(dialogue: list[dict]) -> bytes:
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    combined = AudioSegment.silent(duration=0)

    for turn in dialogue:
        voice_id = VOICE_IDS.get(turn["speaker"], VOICE_IDS["alex"])
        audio_chunks = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5",
            text=turn["line"],
        )
        clip_bytes = b"".join(audio_chunks)
        clip = AudioSegment.from_file(io.BytesIO(clip_bytes), format="mp3")
        combined += clip + AudioSegment.silent(duration=250)

    buffer = io.BytesIO()
    combined.export(buffer, format="mp3")
    return buffer.getvalue()
