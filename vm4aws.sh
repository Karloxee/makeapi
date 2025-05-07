#!/bin/bash
set -e
echo "Installation de VM4 - CI/Terraform"
echo "=================================="
# Mise à jour du système
echo "Mise à jour du système..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget apt-transport-https gnupg lsb-release software-properties-common unzip jq git

# Installation de Java pour Jenkins et SonarQube
echo "Installation de Java..."
# Ajout du dépôt pour OpenJDK
sudo apt install -y default-jdk

# Vérification de l'installation de Java
java -version

# Installation de Jenkins
echo "Installation de Jenkins..."
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo gpg --dearmor -o /usr/share/keyrings/jenkins-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.gpg] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install -y jenkins

# Démarrage du service Jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins
echo "Jenkins est accessible sur http://$(hostname -I | awk '{print $1}'):8080"
echo "Mot de passe initial Jenkins: $(sudo cat /var/lib/jenkins/secrets/initialAdminPassword)"

# Installation de Docker
echo "Installation de Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker jenkins
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Installation de kubectl
echo "Installation de kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# Installation de Terraform
echo "Installation de Terraform..."
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install -y terraform

# Installation de AWS CLI
echo "Installation de AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Installation de SonarQube (en utilisant Docker)
echo "Installation de SonarQube via Docker..."
sudo docker run -d --name sonarqube -p 9000:9000 sonarqube:lts

# Création d'un répertoire pour la configuration K3s
echo "Configuration pour l'accès au cluster K3s..."
mkdir -p $HOME/.kube

echo "======================================"
echo "Installation terminée!"
echo "Jenkins: http://$(hostname -I | awk '{print $1}'):8080"
echo "SonarQube: http://$(hostname -I | awk '{print $1}'):9000"
echo "======================================"
echo "N'oubliez pas de configurer:"
echo "1. AWS avec 'aws configure'"
echo "2. Copier le fichier k3s.yaml depuis le master K3s vers $HOME/.kube/config"
echo "   sur cette machine pour permettre à kubectl et Jenkins d'accéder au cluster"
echo "======================================"
