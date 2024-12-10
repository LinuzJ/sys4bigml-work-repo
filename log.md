# Study/Learning Log for the course project on Dynamic Predictive Edge Offloading

## Introduction

- **12.12.2024**
- **Topics covered**:
  - The topics related to the course project
  - Dynamic Decision-Making for Task Execution Location (Edge vs. Cloud)
  - Use of Machine Learning (Regression) Models for Execution Time Prediction
  - Cloud Compute Design Choices

## Most Important and Relevant Topics Learned

- **Dynamic Prediction Offloading Algorithm**:
  - Uses a linear regression based machine learning model to predict the execution time for the NLP task locally (t_l) versus in the cloud (t_c).
  - Makes close to real-time decisions on where to execute tasks (edge or cloud) to minimize total latency.
- **Focus on NLP Speech-to-Text Tasks**:

  - Input size (e.g., audio transcription length) directly affects compute requirements.
  - Understanding how input size variability influences whether local or cloud processing is optimal.

- **Performance, Consistency, and Reliability**:
  - The primary research question: _How does dynamic prediction offloading affect overall system performance and consistency of offloading choice?_
  - Secondary question: _Do different cloud compute design choices (e.g., serverless platforms vs. fixed servers) influence the reliability of the offloading decisions?_ Note: this secondary question was left unanswered due to time-constraints.
- **Kubernetes and Resource Constraints**:
  - Running “edge” compute in a constrained environment (e.g., Kubernetes pods with limited CPU/Memory).
  - Cloud resources can supplement local computation.

## Critical Points and Areas for Further Discussion

- ## **Model Choice and Performance**:

  - As was demonstrated during the demo, the model currently heavily favors the cloud offloading in the simulated environment.
  - This could partly be due to the simplicity of the linear model. It might not take into account all of the existing complexities in the runtime function of the two possible compute option. Some non-linear option might be of interest in future trials.

- **Scaling to Different Task Types**:

  - Current focus is on NLP speech-to-text. It is not clear whether it would function in the same way for other tasks such as e.g. image classification.
  - task-type-specific models or a general-purpose model needed in the case of other tasks?

- **Cloud Compute Locality**:
  - Currently, the cloud VM is located in the GCP cluster in Finland, `europe-north1`. How would the behavior change if it was move to e.g. `asia-northeast`? This would also be interesting to evaluate.
- **Assumptions**
  - Compute at the edge is resource-constrained (e.g., limited CPU/memory in a Kubernetes pod).
  - Cloud compute is available on demand (e.g., through GCP Cloud Run).
  - Tasks (e.g., NLP speech-to-text processing using OpenAI Whisper) have variable input lengths and thus variable compute requirements.

## Tools, Architectures, and Techniques Evaluated

- **Kubernetes**:
  - Running the edge logic in a Kubernetes pod with restricted resources simulates a real constrained environment.
- **Prometheus and Grafana for Monitoring**:
  - Collect metrics (e.g., task completion times, latency, queue sizes) with Prometheus.
  - Visualize and analyze the offloading decisions and buffers in Grafana dashboards. _Currently not finished_
- **OpenAI Whisper Model**
  - This project uses the [OpenAI Whisper](https://openai.com/index/whisper/) model for NLP speech-to-text.

## Future Potential Study

- **Exploring More Advanced ML Models**:
  - It would be interesting to investigate whether more sophisticated ML methods improve prediction accuracy.
- **Experimenting with Network Conditions**:

  - It would also be interesting to simulate different network latencies and bandwidth fluctuations together with different locations of the Cloud VM to see how the system adapts.
  - This will help in understanding how robust the offloading strategy is in real-world scenarios.

- **Better Monitoring and Observability**:

  - Would be good to implement and create meaningful dashboards that could show the decisions in real-time.
  - By studying time-series data from these visualization, the model for offloading could be tuned and/or the assumptions could be changed to improve the system.

- **Comparing Cloud Deployment Options**:
  - Evaluate how the bootstrapping of purely serverless function calls would affect the system. Bootstrapping here means the loading of the Whisper model.
