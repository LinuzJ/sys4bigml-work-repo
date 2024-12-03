import time
import requests
import numpy as np
import whisper
from queue import Queue
from sklearn.linear_model import LinearRegression
from transcribe_audio import handle_audio, AudioTranscriptionException
from text_analysis import keyword_in_text
from prometheus_client import Counter, Histogram, Gauge

KEYWORD = "police"


class CloudOffloadingException(Exception):
    pass


class PredictiveOffloading:
    def __init__(self, queue_size=10, whisper_model=None, logger=None):
        """
        Initialize the Predictive Offloading system.
        """
        self.logger = logger or self._default_logger()
        self.logger.info("Initializing PredictiveOffloading system...")
        self.queue_size = queue_size
        try:
            self.whisper_model = whisper_model or whisper.load_model("tiny")
            self.logger.info("Whisper model loaded successfully.")
        except Exception as e:
            self.logger.error("Failed to load Whisper model: %s", e)
            raise

        self.local_queue = Queue(maxsize=queue_size)
        self.cloud_queue = Queue(maxsize=queue_size)

        self.local_model = LinearRegression()
        self.cloud_model = LinearRegression()

        self.local_decisions = Counter(
            "local_decisions", "Number of tasks executed locally"
        )
        self.cloud_decisions = Counter(
            "cloud_decisions", "Number of tasks offloaded to the cloud"
        )
        self.local_queue_time = Histogram(
            "local_queue_time", "Time spent in the local queue"
        )
        self.cloud_queue_time = Histogram(
            "cloud_queue_time", "Time spent in the cloud queue"
        )
        self.local_queue_size = Gauge(
            "local_queue_size", "Current size of the local queue"
        )
        self.cloud_queue_size = Gauge(
            "cloud_queue_size", "Current size of the cloud queue"
        )

    def _default_logger(self):
        """Create a default logger if none is passed."""
        import logging

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return logging.getLogger("PredictiveOffloadingDefault")

    def update_queue(self, queue: Queue, time: float, size: int, is_local: bool):
        """
        Update a FIFO queue with new data (time, size).
        """
        self.logger.debug("Updating queue with time=%s, size=%s...", time, size)
        if queue.full():
            queue.get()
        queue.put((time, size))
        self.logger.debug("Queue updated. Current size: %s.", queue.qsize())

        if is_local:
            self.local_queue_time.observe(time)
            self.local_queue_size.set(queue.qsize())
        else:
            self.cloud_queue_time.observe(time)
            self.cloud_queue_size.set(queue.qsize())

    def train_models(self):
        """
        Train local and cloud regression models using queue data.
        """
        self.logger.info("Training local and cloud models...")
        if self.local_queue.qsize() >= 2:
            data_l = list(self.local_queue.queue)
            sizes_l = np.array([d[1] for d in data_l]).reshape(-1, 1)
            times_l = np.array([d[0] for d in data_l])
            self.local_model.fit(sizes_l, times_l)
            self.logger.info("Local model trained successfully.")

        if self.cloud_queue.qsize() >= 2:
            data_c = list(self.cloud_queue.queue)
            sizes_c = np.array([d[1] for d in data_c]).reshape(-1, 1)
            times_c = np.array([d[0] for d in data_c])
            self.cloud_model.fit(sizes_c, times_c)
            self.logger.info("Cloud model trained successfully.")

    def predict_time(self, model, size):
        """
        Predict the time using a given model for a specified data size.
        """
        self.logger.debug(f"Predicting time for size={size}...")
        if not hasattr(model, "coef_"):
            self.logger.debug("Model not trained. Prediction skipped.")
            return None
        prediction = model.predict(np.array([[size]]))[0]
        self.logger.debug(f"Predicted time: {prediction:.2f}")
        return prediction

    def execute_local(self, raw_audio_file: bytes) -> float:
        """
        Simulate execution of the application locally and return execution time.
        """
        self.logger.info("Executing task locally...")
        start = time.time()
        occurences = 0
        try:
            transcription = handle_audio(
                raw_audio_file, whisper_model=self.whisper_model
            )
            occurences = keyword_in_text(transcription, KEYWORD)
        except AudioTranscriptionException as ae:
            self.logger.error(f"Error during transcription: {ae}")

        self.logger.info("Occurrences of '%s': %s", KEYWORD, occurences)
        end = time.time()
        execution_time = end - start

        self.local_decisions.inc()

        self.logger.info("Local execution time: %s seconds", execution_time)
        return execution_time

    def execute_cloud(self, raw_audio_file: bytes, cloud_url: str) -> float:
        """
        Simulate execution of the application on the cloud and return execution time.
        """
        self.logger.info("Offloading task to the cloud with turbo model...")

        headers = {"Content-Type": "application/octet-stream"}

        start = time.time()
        try:
            response = requests.post(
                cloud_url, data=raw_audio_file, headers=headers, timeout=100
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info("Cloud transcription result: %s", result["text"])
        except requests.exceptions.RequestException as e:
            self.logger.error("Error during cloud transcription: %s", e)
            raise CloudOffloadingException(
                "Error during cloud transcription: %s", e
            ) from e

        end = time.time()
        execution_time = end - start

        self.cloud_decisions.inc()

        self.logger.info(
            "Cloud execution time with turbo model: %.2f seconds", execution_time
        )
        return execution_time

    def handle_audiofile(self, raw_audio_file: str, cloud_url: str):
        """
        Handle an incoming application request with input size `size`.
        """
        size = len(raw_audio_file)
        self.logger.info("Handling audio file of size %s bytes...", size)
        self.train_models()

        if not self.local_queue.full() or not self.cloud_queue.full():
            # One or both queues are not full; execute locally and cloud for initial data
            t_l = self.execute_local(raw_audio_file)
            t_c = self.execute_cloud(raw_audio_file, cloud_url)
            self.update_queue(self.local_queue, t_l, size, is_local=True)
            self.update_queue(self.cloud_queue, t_c, size, is_local=False)
            self.logger.info(
                "Executed locally: %s seconds, on cloud: %s seconds", t_l, t_c
            )
            return

        predicted_time_l = self.predict_time(self.local_model, size)
        predicted_time_c = self.predict_time(self.cloud_model, size)

        if predicted_time_l is None or predicted_time_c is None:
            self.logger.warning("Prediction skipped as models are not fully trained.")
            return

        # If predicted local is faster than cloud -> execute locally, else on cloud
        if predicted_time_l < predicted_time_c:
            t_l = self.execute_local(raw_audio_file)
            self.update_queue(self.local_queue, t_l, size, is_local=True)
            self.logger.info("Executed locally: %s seconds", t_l)
        else:
            t_c = self.execute_cloud(raw_audio_file, cloud_url)
            self.update_queue(self.cloud_queue, t_c, size, is_local=False)
            self.logger.info("Executed on cloud: %s seconds", t_c)
