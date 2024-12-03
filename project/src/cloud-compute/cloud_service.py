from flask import Flask, request, jsonify
import whisper
from whisper.audio import log_mel_spectrogram, pad_or_trim
import numpy as np

app = Flask(__name__)

MODEL = whisper.load_model("tiny")


@app.route("/", methods=["POST"])
def transcribe_audio():
    """
    Endpoint to handle transcription of raw audio data sent as binary.
    """
    try:
        audio_data = request.data

        if not audio_data:
            raise ValueError("No audio data received")

        audio_np = np.frombuffer(audio_data, dtype=np.float32)
        audio_np = pad_or_trim(audio_np)
        mel = log_mel_spectrogram(audio_np)
        result = MODEL.transcribe(mel, fp16=False)

        return jsonify({"text": result["text"], "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": "failure"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
