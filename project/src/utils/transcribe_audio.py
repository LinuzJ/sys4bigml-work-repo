import os
import time
import whisper


TRANSCRIPTION_DIR = "./transcriptions"
OUTPUT_DIR = "./received_audio"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)


def save_audio_file(file_data, output_dir, filename="received_audio.wav"):
    """Save the received audio data to a file."""
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "wb") as file:
        file.write(file_data)
    return file_path


def transcribe_audio(file_path: str) -> str:
    """Use OpenAI Whisper to transcribe the audio."""
    print(f"Transcribing audio file: {file_path}")
    model = whisper.load_model("tiny")
    result = model.transcribe(file_path)
    return result["text"]


def save_transcription(transcription, transcription_dir, filename="transcription.txt"):
    """Save the transcription to a file."""
    transcription_path = os.path.join(transcription_dir, filename)
    with open(transcription_path, "w") as file:
        file.write(transcription)
    return transcription_path


def handle_audio(raw_audio_data: bytes, filename="audio.wav") -> str:
    print(f"Received {len(raw_audio_data)} bytes of audio data")

    audio_file_path = save_audio_file(raw_audio_data, OUTPUT_DIR, filename)

    transcription = transcribe_audio(audio_file_path)

    return transcription
