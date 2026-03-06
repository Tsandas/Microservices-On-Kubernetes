sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.35/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.35/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# sudo systemctl enable --now kubelet


# not needed
# sudo nano /etc/netplan/00-installer-config.yaml
# network:
#   ethernets:
#     enp0s3:
#       dhcp4: true          # NAT adapter — keep on DHCP for internet
#     enp0s8:
#       dhcp4: no
#       addresses:
#         - {ipadd}/24
#   version: 2
# sudo netplan apply


# sudo nano /etc/default/kubelet
# KUBELET_EXTRA_ARGS=--node-ip={ipad}


# Create default storage class