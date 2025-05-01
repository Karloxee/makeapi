#!/bin/bash

set -e  # Arrêter le script en cas d'erreur

# Mettre à jour les paquets
sudo apt update && sudo apt upgrade -y

# Installer Java 17 (OpenJDK)
sudo apt install openjdk-17-jdk -y

# Vérifier la version installée
java -version

# Installer unzip si ce n’est pas déjà fait
sudo apt install unzip -y

# Créer l'utilisateur SonarQube s'il n'existe pas
if id "sonar" &>/dev/null; then
    echo "L'utilisateur 'sonar' existe déjà."
else
    sudo useradd -m -d /opt/sonarqube -s /bin/bash sonar
    echo "Définissez un mot de passe pour l'utilisateur sonar :"
    sudo passwd sonar
fi

# Télécharger SonarQube
cd /opt
if [ ! -f sonarqube-25.4.0.105899.zip ]; then
    sudo wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-25.4.0.105899.zip
fi

# Extraire et déplacer
sudo unzip -o sonarqube-25.4.0.105899.zip
sudo rm -rf /opt/sonarqube
sudo mv sonarqube-25.4.0.105899 sonarqube
sudo chown -R sonar:sonar /opt/sonarqube

# Configurer SonarQube pour qu'il se lance avec l'utilisateur sonar
sudo sed -i 's/^#RUN_AS_USER=.*/RUN_AS_USER=sonar/' /opt/sonarqube/bin/linux-x86-64/sonar.sh

# Ajouter les limites système (si non présentes)
grep -qxF "sonar   -   nofile   65536" /etc/security/limits.conf || echo "sonar   -   nofile   65536" | sudo tee -a /etc/security/limits.conf
grep -qxF "sonar   -   nproc    4096" /etc/security/limits.conf || echo "sonar   -   nproc    4096" | sudo tee -a /etc/security/limits.conf

# Créer un service systemd pour SonarQube
sudo tee /etc/systemd/system/sonarqube.service > /dev/null <<EOF
[Unit]
Description=SonarQube service
After=syslog.target network.target

[Service]
Type=forking
ExecStart=/opt/sonarqube/bin/linux-x86-64/sonar.sh start
ExecStop=/opt/sonarqube/bin/linux-x86-64/sonar.sh stop
User=sonar
Group=sonar
Restart=always
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer SonarQube
sudo systemctl daemon-reload
sudo systemctl enable sonarqube
sudo systemctl start sonarqube

# Vérification
sudo systemctl status sonarqube --no-pager

echo "✅ Installation de SonarQube 25.4.0.105899 terminée avec OpenJDK 17 !"
echo "🌐 Accédez à : http://localhost:9000 (admin / admin)"
