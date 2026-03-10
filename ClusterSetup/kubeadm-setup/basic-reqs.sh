# Add host only adapter 
sudo ip link set enp0s8 up
sudo nano /etc/netplan/01-netcfg.yaml
# network:
#   version: 2
#   ethernets:
#     enp0s8:
#       dhcp4: true
sudo netplan apply


sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh


cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
 
sudo modprobe overlay
sudo modprobe br_netfilter


cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
 
sudo sysctl --system


sudo swapoff -a


sudo apt update
sudo apt install -y containerd

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml


# sudo nano /etc/containerd/config.toml
# Find this line (inside [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options])
# SystemdCgroup = false
# Change it to:
# SystemdCgroup = true
# sudo systemctl restart containerd
# sudo systemctl enable containerd
 
# # Verify it is running
# sudo systemctl status containerd
