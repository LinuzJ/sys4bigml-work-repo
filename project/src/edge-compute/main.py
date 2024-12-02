import socket
import whisper
import os
import logging
from offload_ml import PredictiveOffloading

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

HOST = os.getenv("INTERNAL_HOST", "0.0.0.0")
PORT = int(os.getenv("EXPOSE_PORT", "8081"))
BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "4096"))


def start_tcp_server(host, port):
    """Start a TCP server to receive audio files and transcribe them."""
    logger.info("Starting TCP server on %s:%s...", host, port)
    whisper_model = whisper.load_model("tiny")
    predictive_offloading_ml_client = PredictiveOffloading(
        queue_size=5, whisper_model=whisper_model, logger=logger
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        logger.info("Server listening on %s:%s...", host, port)

        while True:
            client_socket, client_address = server_socket.accept()
            logger.info("Connection established with %s", client_address)
            with client_socket:
                # Receive the audio file data
                audio_data = b""
                while True:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                    audio_data += data

                logger.info("Received %s bytes of audio data.", len(audio_data))
                predictive_offloading_ml_client.handle_audiofile(audio_data)


if __name__ == "__main__":
    start_tcp_server(HOST, PORT)
