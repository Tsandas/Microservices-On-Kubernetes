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
# KUBELET_EXTRA_ARGS=--node-ip={ip-ad}

#worker
# kubeadm join .....

# controplane
kubeadm init
sudo kubeadm init --apiserver-advertise-address={ipaddress} --pod-network-cidr=10.244.0.0/16

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/con

# Deploy a cni
# quick deploy kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/calico.yaml
# Create default storage class
# kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml
# kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# Ingress controller Nginx (Bare metal)
# kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.14.0/deploy/static/provider/baremetal/deploy.yaml 
# check ingress-nginx controller svc and portforward 

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