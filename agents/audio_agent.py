import os
import uuid
from pathlib import Path
import pyttsx3
from gtts import gTTS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the audio directory exists
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)

def generate_audio_filename(base: str = None) -> str:
    """
    Generates a unique filename for the audio file.
    
    Args:
        base (str): Optional base name for the file. If None, a UUID is generated.

    Returns:
        str: The generated audio filename with .mp3 extension.
    """
    return f"{base or uuid.uuid4().hex}.mp3"

def generate_audio(text: str, filename: str = None, engine: str = "gtts") -> Path:
    """
    Converts input text to speech and saves it as an audio file.
    
    Args:
        text (str): The input text to convert to speech.
        filename (str): Optional filename for the audio file (without extension). If None, a UUID is used.
        engine (str): The text-to-speech engine to use ('gtts' or 'pyttsx3').

    Returns:
        Path: Path to the generated audio file.
    """
    # Generate audio filename (with .mp3 extension)
    filename = generate_audio_filename(filename)
    audio_path = AUDIO_DIR / filename

    try:
        # Generate audio using gTTS (Google Text-to-Speech)
        if engine.lower() == "gtts":
            tts = gTTS(text)
            tts.save(str(audio_path))
        # Generate audio using pyttsx3
        elif engine.lower() == "pyttsx3":
            engine = pyttsx3.init()
            engine.save_to_file(text, str(audio_path))
            engine.runAndWait()
        else:
            raise ValueError("Invalid engine type. Use 'gtts' or 'pyttsx3'.")

        # Log the successful generation of audio
        logger.info(f"Audio generated at: {audio_path}")
        return audio_path

    except Exception as e:
        # Log any errors that occur during audio generation
        logger.error(f"Failed to generate audio: {e}")
        return None
