# Optional Kubernetes / Minikube deployment

This project is a batch analyzer rather than a long-running service, so Kubernetes `Job` is a better fit than `Deployment`.

Example with Minikube:

```bash
docker build -t dsoc-evidence-analyzer:latest .
minikube image load dsoc-evidence-analyzer:latest
kubectl apply -f k8s/job.yaml
kubectl logs job/dsoc-evidence-analyzer
kubectl delete job dsoc-evidence-analyzer
```

The manifest sets `imagePullPolicy: Never` because the image is loaded directly into the local Minikube environment.
