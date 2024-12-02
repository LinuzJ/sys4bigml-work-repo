import socket
import whisper
import os

# Configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 8081  # Port to listen on
BUFFER_SIZE = 4096  # Size of the buffer for receiving data


def save_audio_file(file_data, output_dir, filename="received_audio.wav"):
    """Save the received audio data to a file."""
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "wb") as file:
        file.write(file_data)
    return file_path


def transcribe_audio(file_path):
    """Use OpenAI Whisper to transcribe the audio."""
    print(f"Transcribing audio file: {file_path}")
    model = whisper.load_model("base")  # Use the base model
    result = model.transcribe(file_path)
    return result["text"]


def save_transcription(transcription, transcription_dir, filename="transcription.txt"):
    """Save the transcription to a file."""
    transcription_path = os.path.join(transcription_dir, filename)
    with open(transcription_path, "w") as file:
        file.write(transcription)
    return transcription_path


def start_tcp_server(host, port):
    """Start a TCP server to receive audio files and transcribe them."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server listening on {host}:{port}...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection established with {client_address}")
            with client_socket:
                # Receive the audio file data
                audio_data = b""
                while True:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                    audio_data += data


if __name__ == "__main__":
    start_tcp_server(HOST, PORT)
