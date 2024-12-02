from flask import Flask, request, jsonify
import whisper

app = Flask(__name__)

model = whisper.load_model("turbo")


@app.route("/", methods=["POST"])
def transcribe_audio():
    try:
        audio_data = request.data
        result = model.transcribe(audio_data, fp16=False)
        return jsonify({"text": result["text"], "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": "failure"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
