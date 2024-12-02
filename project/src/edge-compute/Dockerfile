FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/received_audio /app/transcriptions

EXPOSE 8081

CMD ["python", "task_executor.py"]