import asyncio

import streamlit as st
from gradium import GradiumClient
from gradium import speech as gradium_speech
from gradium import usages as gradium_usages
from gradium import voices as gradium_voices

_client = GradiumClient(api_key=st.secrets["GRADIUM_API_KEY"])


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


def get_voices(include_catalog: bool = True) -> list[dict]:
    """Get all available voices (custom + catalog)."""
    result = _run(gradium_voices.get(_client, include_catalog=include_catalog))
    if isinstance(result, dict):
        return result.get("voices", result.get("items", [result]))
    return result if isinstance(result, list) else []


def get_credits() -> dict:
    """Get remaining credits info."""
    return _run(gradium_usages.get(_client))


def generate_tts(
    text: str,
    voice_id: str,
    output_format: str = "wav",
    padding_bonus: float = 0.0,
    temp: float = 0.7,
    cfg_coef: float = 2.0,
) -> bytes:
    """Generate TTS audio and return raw bytes."""
    setup = {
        "voice_id": voice_id,
        "output_format": output_format,
        "json_config": {
            "padding_bonus": padding_bonus,
            "temp": temp,
            "cfg_coef": cfg_coef,
        },
    }
    result = _run(gradium_speech.tts(_client, setup, text))
    return result.raw_data
