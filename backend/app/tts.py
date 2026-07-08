import io
import os
import tempfile
from pathlib import Path

from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

_local_ffmpeg = Path(__file__).parent.parent / "tools" / "ffmpeg.exe"
if _local_ffmpeg.exists():
    AudioSegment.converter = str(_local_ffmpeg)

VOICE_IDS = {
    "alex": os.environ.get("ELEVENLABS_VOICE_ALEX", "21m00Tcm4TlvDq8ikWAM"),
    "sam": os.environ.get("ELEVENLABS_VOICE_SAM", "AZnzlk1XvdvUeBnXmlld"),
}

# Distinct built-in Windows SAPI voices to approximate two speakers when
# no ElevenLabs key is available. Falls back to whatever voice is first
# on the system if only one is installed.
_LOCAL_VOICE_HINTS = {
    "alex": "David",
    "sam": "Zira",
}


def render_dialogue_to_audio(dialogue: list[dict]) -> bytes:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        return _render_dialogue_locally(dialogue)

    try:
        return _render_dialogue_with_elevenlabs(dialogue, api_key)
    except Exception as exc:
        # Key missing/invalid/out of quota, etc. Fall back so the pipeline
        # is still testable end-to-end without a working ElevenLabs account.
        print(f"[tts] ElevenLabs call failed ({exc}); falling back to local TTS")
        return _render_dialogue_locally(dialogue)


def _render_dialogue_with_elevenlabs(dialogue: list[dict], api_key: str) -> bytes:
    client = ElevenLabs(api_key=api_key)
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


def _render_dialogue_locally(dialogue: list[dict]) -> bytes:
    """Offline stand-in for ElevenLabs using the OS's built-in SAPI voices
    (via pyttsx3). No API key required. Quality is far below ElevenLabs —
    this exists only so the pipeline is testable without a key."""
    import pythoncom
    import pyttsx3

    # FastAPI runs sync endpoints in a worker thread, and pyttsx3's SAPI5
    # driver needs an explicit COM apartment on that thread or engine calls
    # hang indefinitely.
    pythoncom.CoInitialize()
    try:
        # pyttsx3.init() caches a single engine in a module-level weak-value
        # dict; as long as any reference to it is alive, later init() calls
        # return that same (already-used) engine instead of a fresh one, and
        # its SAPI5 driver hangs on a second runAndWait(). So we pull voice
        # metadata into plain tuples and drop the probe engine immediately,
        # then create + drop a new engine per turn.
        probe_engine = pyttsx3.init()
        voice_options = [(v.id, v.name) for v in probe_engine.getProperty("voices")]
        probe_engine.stop()
        del probe_engine

        def pick_voice_id(speaker: str) -> str | None:
            hint = _LOCAL_VOICE_HINTS.get(speaker, "")
            for voice_id, voice_name in voice_options:
                if hint.lower() in voice_name.lower():
                    return voice_id
            return voice_options[0][0] if voice_options else None

        combined = AudioSegment.silent(duration=0)

        for turn in dialogue:
            engine = pyttsx3.init()
            voice_id = pick_voice_id(turn["speaker"])
            if voice_id:
                engine.setProperty("voice", voice_id)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            engine.save_to_file(turn["line"], tmp_path)
            engine.runAndWait()
            engine.stop()
            del engine

            clip = AudioSegment.from_file(tmp_path, format="wav")
            os.remove(tmp_path)
            combined += clip + AudioSegment.silent(duration=250)
    finally:
        pythoncom.CoUninitialize()

    buffer = io.BytesIO()
    combined.export(buffer, format="mp3")
    return buffer.getvalue()
