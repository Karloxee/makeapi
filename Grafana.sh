#!/bin/bash

echo "🚀 Début de l'installation de Grafana sur Debian..."

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des prérequis
sudo apt install -y software-properties-common wget apt-transport-https

# Ajout de la clé GPG pour le dépôt Grafana
echo "🔑 Ajout de la clé GPG Grafana..."
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# Ajout du dépôt officiel de Grafana
echo "📦 Ajout du dépôt Grafana..."
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Mise à jour et installation de Grafana
echo "💾 Installation de Grafana..."
sudo apt update
sudo apt install -y grafana

# Démarrage et activation du service Grafana
echo "🚀 Démarrage du service Grafana..."
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Vérification du statut du service
echo "📡 Vérification du statut Grafana..."
sudo systemctl status grafana-server --no-pager

echo "✅ Installation de Grafana terminée avec succès !"
echo "🌐 Accédez à Grafana via : http://localhost:3000"
echo "🔑 Connexion par défaut : admin / admin"
