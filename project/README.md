Needed to run:

- minikube
- mount to minikube VM
- Cloudrun service
- env config map tp url (`kubectl create configmap edge-compute-config --from-env-file=.env`)
- prometheus port forwarding to local machine (`kubectl port-forward service/prometheus 9090:9090`)
