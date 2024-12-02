FROM python:3.10-slim

WORKDIR /app

# System deps for Whisper
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8081

CMD ["python", "main.py"]