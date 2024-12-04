import socket
import os

EDGE_COMPUTE_HOST = os.getenv("EDGE_COMPUTE_HOST", "edge-compute-service")
EDGE_COMPUTE_PORT = int(os.getenv("EDGE_COMPUTE_PORT", "8081"))

BUFFER_SIZE = int(os.getenv("BUFFER_SIZE", "4096"))

AUDIO_FOLDER = os.getenv("AUDIO_PATH", "/app/audio")


class SendingAudioException(Exception):
    pass


def send_audio_file(file_path):
    """Send a single audio file to the edge-compute container."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((EDGE_COMPUTE_HOST, EDGE_COMPUTE_PORT))
            print(f"Connected to edge-compute: {EDGE_COMPUTE_HOST}:{EDGE_COMPUTE_PORT}")

            with open(file_path, "rb") as file:
                while chunk := file.read(BUFFER_SIZE):
                    client_socket.sendall(chunk)

            print(f"File '{file_path}' sent successfully.")
    except Exception as e:
        raise SendingAudioException(f"Failed to send file '{file_path}': {e}")


def main():
    """Main function to send all audio files in the specified folder."""
    if not os.path.exists(AUDIO_FOLDER):
        print(f"Audio folder '{AUDIO_FOLDER}' does not exist.")
        return

    files = [
        f
        for f in os.listdir(AUDIO_FOLDER)
        if os.path.isfile(os.path.join(AUDIO_FOLDER, f))
    ]
    if not files:
        print(f"No audio files found in '{AUDIO_FOLDER}'.")
        return

    print(
        f"Found {len(files)} audio file(s) in '{AUDIO_FOLDER}'. Sending to edge-compute..."
    )
    while True:
        for file_name in files:
            if not file_name[-3:] == "wav":
                print("Incorrect file format for file: %s", file_name)
                continue
            try:
                file_path = os.path.join(AUDIO_FOLDER, file_name)
                send_audio_file(file_path)
            except SendingAudioException as e:
                print(f"Error while sending files: {e}")
            except Exception as unknown_e:
                print(f"Unknown Error while sending files: {unknown_e}")


if __name__ == "__main__":
    main()
