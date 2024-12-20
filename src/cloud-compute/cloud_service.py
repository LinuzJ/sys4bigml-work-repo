import logging
import whisper
import os
import numpy as np
from flask import Flask, request, jsonify
from whisper.audio import log_mel_spectrogram, pad_or_trim

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL = whisper.load_model("tiny")

OUTPUT_DIR = "./received_audio"

os.makedirs(OUTPUT_DIR, exist_ok=True)


class AudioTranscriptionException(Exception):
    pass


class ModelMissingException(AudioTranscriptionException):
    pass


class SavingFailedException(AudioTranscriptionException):
    pass


def save_audio_file(file_data, output_dir, filename="received_audio.wav") -> str:
    """Save the received audio data to a file."""
    try:
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "wb") as file:
            file.write(file_data)
        return file_path
    except Exception as e:
        raise SavingFailedException(f"Somethign went wrong while saving: {e}") from e


def remove_audio_file(filename: str):
    os.remove(filename)


def transcribe_audio(file_path: str, model) -> str:
    """Use OpenAI Whisper to transcribe the audio."""
    print(f"Transcribing audio file: {file_path}")
    results = ""
    try:
        text = model.transcribe(file_path, fp16=False)
        results = text["text"]
    except Exception as e:
        raise AudioTranscriptionException(f"Error while transcribing: {e}") from e
    return results


@app.route("/", methods=["POST"])
def transcribe_audio_endpoint():
    """
    Endpoint to handle transcription of raw audio data sent as binary.
    """
    try:
        audio_data = request.data

        if not audio_data:
            logger.exception("No audio data recived")
            return

        logger.info("Recieved request of length %s", len(audio_data))
        audio_file_path = save_audio_file(
            audio_data,
            OUTPUT_DIR,
        )
        logger.info("Saved audiofile")
        result = MODEL.transcribe(audio_file_path, fp16=False)
        remove_audio_file(audio_file_path)
        logger.info("Audio transcribed to: %s", result)

        return jsonify({"text": result["text"], "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": "failure"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
