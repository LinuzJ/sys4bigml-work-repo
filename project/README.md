### Dynamic Predictive Edge Offloading

This project presents an MVP of a complete edge based NLP processing system. In the real world this could be some speech detection on some compute-restricted edge device with a network connection.

The purpose is to dynamically evaluate whether or not the NLP processing, OpenAI Whisper in this case, should be executed locally or be offloaded to a Cloud instance performing the same computation with more resources.

#### Tools

This MVP is built using:

- Kubernetes
- Minikube
- Docker
- Python
- Flask
- scikit-learn
- OpenAI Whisper
- Prometheus
- Grafana

#### Running

To run locally, follow the proceeding steps:

- minikube
- mount to minikube VM
- Cloudrun service
- prometheus port forwarding to local machine (`kubectl port-forward service/prometheus 9090:9090`)
