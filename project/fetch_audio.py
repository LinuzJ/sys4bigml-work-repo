import requests
import time
import os
import random

sample_text = (
    "Once upon a time in a land far, far away, there was a kingdom where magic was commonplace. "
    "The people lived in harmony with the mystical creatures that roamed the forests and mountains. "
    "Every year, they celebrated the Festival of Lights, a grand event that brought joy to all. "
    "Legends spoke of a hidden treasure guarded by a dragon, waiting for a hero to claim it. "
    "This is the tale of how courage and friendship can overcome even the greatest of challenges."
)


def generate_story(word_count):
    """Generate a story with the specified word count."""
    words = sample_text.split()
    repeated_words = words * ((word_count // len(words)) + 1)
    story_words = repeated_words[:word_count]
    story = " ".join(story_words)
    return story


def create_sound(text):
    """Send a POST request to create a sound and return the sound ID."""
    payload = {"engine": "Google", "data": {"text": text, "voice": "en-AU"}}
    try:
        response = requests.post("https://api.soundoftext.com/sounds", json=payload)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("success"):
            sound_id = response_json.get("id")
            print(sound_id)
            return sound_id
        else:
            print("Failed to create sound.")
            return None
    except Exception as e:
        print(f"Exception during create_sound: {e}")
        return None


def check_status(sound_id):
    """Check the status of the sound processing."""
    url = f"https://api.soundoftext.com/sounds/{sound_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
        return response_json
    except Exception as e:
        print(f"Exception during check_status: {e}")
        return None


def download_audio(location, filepath):
    """Download the audio file from the provided location."""
    try:
        response = requests.get(location)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Saved audio file: {filepath}")
    except Exception as e:
        print(f"Exception during download_audio: {e}")


def main():
    # Generate 50 word counts evenly distributed between 10 and 400 words
    word_counts = [
        int(10 + i * (390 / 49)) for i in range(50)
    ]  # Generates numbers from 10 to 400
    output_dir = "output_stories"
    os.makedirs(output_dir, exist_ok=True)

    for _ in range(50):
        word_count = random.randint(20, 150)
        print(f"Processing story with {word_count} words.")
        story = generate_story(word_count)
        sound_id = create_sound(story)

        if sound_id:
            status = ""
            max_attempts = 24  # Maximum attempts to check status (1 minute total)
            attempts = 0
            while status != "Done" and attempts < max_attempts:
                time.sleep(5)
                status_response = check_status(sound_id)
                if status_response:
                    status = status_response.get("status")
                    if status == "Done":
                        location = status_response.get("location")
                        filename = f"story_{word_count}_words.mp3"
                        filepath = os.path.join(output_dir, filename)
                        download_audio(location, filepath)
                        break  # Exit the loop after successful download
                    elif status == "Failed":
                        print(f"Processing failed for story with {word_count} words.")
                        break
                    else:
                        print(f"Status for story with {word_count} words: {status}")
                else:
                    print(f"Failed to get status for story with {word_count} words.")
                    break
                attempts += 1
            if attempts >= max_attempts:
                print(f"Maximum attempts reached for story with {word_count} words.")
        else:
            print(f"Failed to create sound for story with {word_count} words.")


if __name__ == "__main__":
    main()
