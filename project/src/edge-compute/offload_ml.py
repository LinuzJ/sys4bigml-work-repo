import time
import numpy as np
from queue import Queue
from sklearn.linear_model import LinearRegression
from transcribe_audio import handle_audio
from text_analysis import keyword_in_text


KEYWORD = "police"


class PredictiveOffloading:
    def __init__(self, queue_size=10):
        """
        Initialize the Predictive Offloading system.

        Args:
        - queue_size (int): Maximum size for FIFO queues B_l (local) and B_c (cloud).
        - threshold (float): Threshold time to decide offloading.
        """
        self.queue_size = queue_size

        self.local_queue = Queue(maxsize=queue_size)
        self.cloud_queue = Queue(maxsize=queue_size)

        self.local_model = LinearRegression()
        self.cloud_model = LinearRegression()

    def update_queue(self, queue, time, size):
        """
        Update a FIFO queue with new data (time, size).
        If the queue is full, the oldest item is removed.
        """
        if queue.full():
            queue.get()
        queue.put((time, size))

    def train_models(self):
        """
        Train local and cloud regression models using queue data.
        """
        if self.local_queue.qsize() >= 2:
            data_l = list(self.local_queue.queue)
            sizes_l = np.array([d[1] for d in data_l]).reshape(-1, 1)
            times_l = np.array([d[0] for d in data_l])
            self.local_model.fit(sizes_l, times_l)

        if self.cloud_queue.qsize() >= 2:
            data_c = list(self.cloud_queue.queue)
            sizes_c = np.array([d[1] for d in data_c]).reshape(-1, 1)
            times_c = np.array([d[0] for d in data_c])
            self.cloud_model.fit(sizes_c, times_c)

    def predict_time(self, model, size):
        """
        Predict the time using a given model for a specified data size.
        Returns None if the model is not trained.
        """
        if not hasattr(model, "coef_"):
            return None
        return model.predict(np.array([[size]]))[0]

    def execute_local(self, raw_audio_file: bytes) -> float:
        """
        Simulate execution of the application locally and return execution time.
        """
        start = time.time()

        transcription = handle_audio(raw_audio_file)
        occurences = keyword_in_text(transcription, KEYWORD)

        print(occurences)

        end = time.time()
        return end - start

    def execute_cloud(self, raw_audio_file: bytes) -> float:
        """
        Simulate execution of the application on the cloud and return execution time.
        """
        execution_time = self.execute_local(raw_audio_file) * 0.8
        return execution_time

    def handle_audiofile(self, raw_audio_file: str):
        """
        Handle an incoming application request with input size `size`.
        """
        size = len(raw_audio_file)
        self.train_models()

        if not self.local_queue.full() or not self.cloud_queue.full():
            # One or both queues are not full; execute locally and cloud for initial data
            t_l = self.execute_local(raw_audio_file)
            t_c = self.execute_cloud(raw_audio_file)
            self.update_queue(self.local_queue, t_l, size)
            self.update_queue(self.cloud_queue, t_c, size)
            print(f"Executed locally: {t_l:.2f} seconds, on cloud: {t_c:.2f} seconds")
            return

        predicted_time_l = self.predict_time(self.local_model, size)
        predicted_time_c = self.predict_time(self.cloud_model, size)

        if predicted_time_l is None or predicted_time_c is None:
            return

        # If predicted local is faster than cloud -> execute locally, else on cloud
        if predicted_time_l < predicted_time_c:
            t_l = self.execute_local(raw_audio_file)
            self.update_queue(self.local_queue, t_l, size)
            print(f"Executed locally: {t_l:.2f} seconds")
        else:
            t_c = self.execute_cloud(raw_audio_file)
            self.update_queue(self.cloud_queue, t_c, size)
            print(f"Executed on cloud: {t_c:.2f} seconds")
