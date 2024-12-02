import socket
import whisper
import os
from offload_ml import PredictiveOffloading

HOST = os.getenv("INTERNAL_HOST", "0.0.0.0")
PORT = int(os.getenv("EXPOSE_PORT", "8081"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "4096"))


def start_tcp_server(host, port):
    """Start a TCP server to receive audio files and transcribe them."""
    predictive_offloading_ml_client = PredictiveOffloading(queue_size=5)

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

                predictive_offloading_ml_client.handle_audiofile(audio_data)


if __name__ == "__main__":
    start_tcp_server(HOST, PORT)
