#!/bin/bash

set -e  # Arrêter le script en cas d'erreur

echo "🚀 Installation de Terraform..."

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des prérequis
sudo apt install -y curl unzip

# Détection de la dernière version de Terraform
LATEST_VERSION=$(curl -s https://api.github.com/repos/hashicorp/terraform/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
echo "📦 Dernière version détectée : Terraform $LATEST_VERSION"

# Téléchargement de Terraform
curl -LO "https://releases.hashicorp.com/terraform/${LATEST_VERSION}/terraform_${LATEST_VERSION}_linux_amd64.zip"

# Extraction et déplacement du binaire
unzip "terraform_${LATEST_VERSION}_linux_amd64.zip"
sudo mv terraform /usr/local/bin/

# Vérification de l'installation
terraform version

# Nettoyage des fichiers temporaires
rm -f "terraform_${LATEST_VERSION}_linux_amd64.zip"

echo "✅ Terraform installé avec succès !"
