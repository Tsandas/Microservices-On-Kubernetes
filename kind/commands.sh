kind load docker-image <image-name> --name <cluster-name>

kind load docker-image myapp:latest --name kind --nodes kind-worker


nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.1/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx edit deployment ingress-nginx-controller
remove         ingress-ready: "true"



kubectl port-forward -n ingress-nginx pod/ingress-nginx-controller-7d45bb6d5d-gmcjh 80:80