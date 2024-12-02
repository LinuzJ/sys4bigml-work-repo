import whisper
import time
import os

model = whisper.load_model("tiny")
files = os.listdir("../audio")

for audio_file in files:
    s = time.time()
    file = f"../audio/{audio_file}"
    result = model.transcribe(file, fp16=False)
    e = time.time()

    print(f"Transcribed text: {result["text"]} in {round(e - s, 4)} seconds")
