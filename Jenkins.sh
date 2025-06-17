#!/bin/bash

echo "Début de l'installation de Jenkins sur Debian..."

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de dépendances nécessaires
echo "Installation des dépendances (curl, gpg, Java)..."
sudo apt install -y curl gnupg2 openjdk-17-jdk

# Vérification de Java
java -version || { echo "Java 17 n'a pas été installé correctement !"; exit 1; }

# Nettoyage d'anciennes sources ou clés Jenkins (au cas où)
echo "Nettoyage des anciennes sources Jenkins..."
sudo rm -f /etc/apt/sources.list.d/jenkins.list
sudo rm -f /usr/share/keyrings/jenkins-keyring.*

# Ajout de la clé GPG correcte pour le dépôt Jenkins
echo "Ajout de la clé GPG Jenkins (format gpg)..."
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | \
  gpg --dearmor | sudo tee /usr/share/keyrings/jenkins-keyring.gpg > /dev/null

# Ajout du dépôt Jenkins
echo "Ajout du dépôt officiel Jenkins..."
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.gpg] https://pkg.jenkins.io/debian-stable binary/" | \
  sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

# Mise à jour et installation de Jenkins
echo "Mise à jour des paquets..."
sudo apt update
echo "Installation de Jenkins..."
sudo apt install -y jenkins || { echo "Échec de l'installation de Jenkins ! Vérifiez les sources."; exit 1; }

# Démarrage et activation de Jenkins
echo "Démarrage de Jenkins..."
sudo systemctl start jenkins
sudo systemctl enable jenkins
systemctl status jenkins --no-pager

# Vérification et affichage du mot de passe initial
JENKINS_PASSWORD_FILE="/var/lib/jenkins/secrets/initialAdminPassword"
if [ -f "$JENKINS_PASSWORD_FILE" ]; then
    echo "Mot de passe initial Jenkins : $(sudo cat $JENKINS_PASSWORD_FILE)"
else
    echo "Impossible de récupérer le mot de passe initial. Jenkins a-t-il bien démarré ?"
fi

echo "Jenkins est installé et fonctionne sur http://localhost:8080"





