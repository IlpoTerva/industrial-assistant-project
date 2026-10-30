from piper import PiperVoice
from app.config import settings
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class VoiceFiles:
    name: str
    model: Path=None
    config: Path=None


def _resolve_voice(name: str, dir: str)-> VoiceFiles:
    voiceFiles = VoiceFiles(name=name.split("_")[0])
    for file in os.listdir(dir):
        if file.endswith(".onnx"):
            voiceFiles.model = os.path.join(dir, file)
        if file.endswith(".json"):
            voiceFiles.config = os.path.join(dir, file)
    return voiceFiles

def load_voice(lang: list[str]|str) -> dict[str, PiperVoice]:
    if isinstance(lang, str):
        lang = [lang]
    voices = {}
    for l in lang:
        voiceFiles = _resolve_voice(name=settings.VOICE_FILE[l], dir=settings.VOICE_DIR[l])
        voices[l] = PiperVoice.load(model_path=voiceFiles.model, config_path=voiceFiles.config)
    return voices


