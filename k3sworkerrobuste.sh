#!/bin/bash
set -e  # Arrêt en cas d'erreur

# 🔹 Variables
K3S_URL="https://192.168.27.159:6443"
K3S_TOKEN="K102bfd094c59f0d770712eea9cd4dd14304556e8471f577d469a9f04e0cc353d5e::server:146dfeb288f17e803ed87b2e69541c3e"

echo "🚀 Installation du client K3s (agent)..."

# 🔹 Correction DNS si nécessaire
echo "📡 Vérification de la connectivité réseau..."
if ! ping -c 1 8.8.8.8 >/dev/null; then
    echo "⚠ Aucune connexion Internet. Vérifie ta passerelle réseau."
    exit 1
fi

if ! ping -c 1 deb.debian.org >/dev/null; then
    echo "⚠ Résolution DNS échouée. Ajout de Google DNS..."
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
fi

# 🔹 Mise à jour système
echo "🔄 Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# 🔹 Suppression d'une éventuelle ancienne install
sudo systemctl stop k3s-agent || true
sudo /usr/local/bin/k3s-uninstall.sh || true
sudo rm -rf /etc/rancher

# 🔹 Installation de K3s agent
echo "📦 Téléchargement et installation de K3s agent..."
curl -sfL https://get.k3s.io | K3S_URL=$K3S_URL K3S_TOKEN=$K3S_TOKEN sh -s - agent --node-name client-k3s

# 🔹 Vérification du service
echo "🔍 Vérification du service k3s-agent..."
if systemctl list-units --type=service | grep -q "k3s-agent"; then
    sudo systemctl enable --now k3s-agent
    sudo systemctl status k3s-agent --no-pager
else
    echo "❌ Le service k3s-agent n’a pas été installé. Installation échouée."
    exit 1
fi

# 🔹 Vérification de l'intégration dans le cluster
echo "🔗 Vérification de la connexion au cluster..."
sudo k3s kubectl get nodes || echo "⚠ Attention : le client K3s n'est peut-être pas encore reconnu."

echo "✅ Client K3s installé avec succès ! 🎉"
