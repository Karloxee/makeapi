#!/bin/bash
set -e  # Arrêter l'exécution en cas d'erreur

# 🔹 Variables
K3S_URL="https://192.168.27.144:6443"  # Remplace par l'IP de ton maître K3S !
K3S_TOKEN="K100efd1126ae5dc02fc9d6bd64a7f4928043d20430ba08e099ef524dfe79fcc665::server:76589f873c726efc4eb73fde7f76cbaa"
# Rentre sudo cat /var/lib/rancher/k3s/server/node-token sur ta machine maître pour avoir le token !

echo "🚀 Installation du client K3s (agent)..."

# 🔹 Mise à jour du système
sudo apt update && sudo apt upgrade -y

# 🔹 Installation du client K3s
echo "📦 Téléchargement et installation de K3s agent..."
if ! curl -sfL https://get.k3s.io | K3S_URL=$K3S_URL K3S_TOKEN=$K3S_TOKEN sh -s - --node-name client-k3s; then
    echo "❌ Erreur lors de l'installation du client K3s."
    exit 1
fi

# 🔹 Vérification du service K3s
echo "🔍 Vérification de l'état du client K3s..."
sudo systemctl enable --now k3s-agent
sudo systemctl status k3s-agent --no-pager

# 🔹 Vérification de la connexion au serveur K3s
echo "📡 Vérification de l'intégration du client dans le cluster..."
kubectl get nodes || echo "⚠ Attention : le client K3s n'est peut-être pas encore reconnu."

echo "✅ Client K3s installé avec succès ! 🎉"
