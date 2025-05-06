#!/bin/bash

set -e

echo "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

echo "Installation des dépendances..."
sudo apt install -y curl wget apt-transport-https gnupg lsb-release software-properties-common

echo "Installation de K3s (serveur)..."
curl -sfL https://get.k3s.io | sh -s - server \
  --write-kubeconfig-mode 644 \
  --node-name k3s-master

echo "Vérification de l'état du cluster K3s..."
if ! sudo k3s kubectl get nodes; then
    echo "Erreur lors de l'installation de K3s."
    exit 1
fi

echo "Ajout de KUBECONFIG pour l'utilisateur courant..."
mkdir -p $HOME/.kube
sudo cp /etc/rancher/k3s/k3s.yaml $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Vérification de la configuration KUBECONFIG
if ! kubectl get nodes; then
    echo "KUBECONFIG n'est pas correctement configuré."
    exit 1
fi

echo "Installation de Helm..."
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Vérification de Helm
if ! helm version; then
    echo "Erreur lors de l'installation de Helm."
    exit 1
fi

echo "Installation de cert-manager via Helm..."
kubectl create namespace cert-manager || true

helm repo add jetstack https://charts.jetstack.io/
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true

echo "Attente du déploiement de cert-manager..."
kubectl rollout status deployment cert-manager -n cert-manager || {
    echo "Erreur lors du déploiement de cert-manager."
    exit 1
}

echo "Vérification des pods cert-manager..."
kubectl get pods -n cert-manager

echo "VM1 prête avec K3s, Helm et cert-manager"
