#!/bin/bash
set -e  # Arrêt en cas d'erreur

# Variables
K3S_URL="https://192.168.27.144:6443" #IP Machine Maître 
K3S_TOKEN="K100efd1126ae5dc02fc9d6bd64a7f4928043d20430ba08e099ef524dfe79fcc665::server:76589f873c726efc4eb73fde7f76cbaa"
# Faire sudo cat /var/lib/rancher/k3s/server/node-token sur ta machine maître pour avoir le token 

echo "Installation du client K3s (agent)..."

# Correction DNS si nécessaire
echo "Vérification de la connectivité réseau..."
if ! ping -c 1 8.8.8.8 >/dev/null; then
    echo "Aucune connexion Internet. Vérifie ta passerelle réseau."
    exit 1
fi

if ! ping -c 1 deb.debian.org >/dev/null; then
    echo "Résolution DNS échouée. Ajout de Google DNS..."
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
fi

# Mise à jour système
echo "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# Suppression d'une éventuelle ancienne install
sudo systemctl stop k3s-agent || true
sudo /usr/local/bin/k3s-uninstall.sh || true
sudo rm -rf /etc/rancher

# Installation de K3s agent
echo "Téléchargement et installation de K3s agent..."
curl -sfL https://get.k3s.io | K3S_URL=$K3S_URL K3S_TOKEN=$K3S_TOKEN sh -s - agent --node-name client-k3s

# Vérification du service
echo "🔍 Vérification du service k3s-agent..."
if systemctl list-units --type=service | grep -q "k3s-agent"; then
    sudo systemctl enable --now k3s-agent
    sudo systemctl status k3s-agent --no-pager
else
    echo "Le service k3s-agent n’a pas été installé. Installation échouée."
    exit 1
fi

# Vérification de l'intégration dans le cluster
echo "Vérification de la connexion au cluster..."
sudo k3s kubectl get nodes || echo "⚠ Attention : le client K3s n'est peut-être pas encore reconnu."

echo "Client K3s installé avec succès ! "
