import socket
import os

EDGE_COMPUTE_HOST = "edge-compute"
EDGE_COMPUTE_PORT = 8081
BUFFER_SIZE = 4096
AUDIO_FOLDER = "./audio"


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
        print(f"Failed to send file '{file_path}': {e}")


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

    for file_name in files:
        file_path = os.path.join(AUDIO_FOLDER, file_name)
        send_audio_file(file_path)


if __name__ == "__main__":
    main()
