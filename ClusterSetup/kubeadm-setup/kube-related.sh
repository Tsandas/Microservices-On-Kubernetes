sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.35/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.35/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# it wont run if cluster not setup, in nodes
# sudo systemctl enable --now kubelet

# sudo nano /etc/default/kubelet
# KUBELET_EXTRA_ARGS=--node-ip={ipad}

# Create default storage class

# Tip
# If u want metrics from kube-scheduler, control-manager, etcd
# Make sure to change these default settings
# sudo vi /etc/kubernetes/manifests/kube-controller-manager.yaml
# sudo vi /etc/kubernetes/manifests/kube-scheduler.yaml
# sudo vi /etc/kubernetes/manifests/etcd.yaml

# - --bind-address=127.0.0.1
# change to:
# - --bind-address=0.0.0.0
# - --listen-metrics-urls=http://127.0.0.1:2381
# change to:
# - --listen-metrics-urls=http://0.0.0.0:2381

# For proxy, but if u use calico probably kubeproxy is not enabled
# kubectl edit configmap kube-proxy -n kube-system
# change:
# metricsBindAddress: ""
# to:
# metricsBindAddress: "0.0.0.0:10249"
# kubectl rollout restart daemonset kube-proxy -n kube-system