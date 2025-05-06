#!/bin/bash

set -e  # Arrêter le script en cas d'erreur

echo "🚀 Début de l'installation de SonarQube avec PostgreSQL sur Debian..."

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Java 17 (OpenJDK)
echo "🔧 Installation de Java 17..."
sudo apt install openjdk-17-jdk -y
java -version || { echo "❌ Java 17 n'a pas été installé correctement !"; exit 1; }

# Installation de PostgreSQL
echo "🛠 Installation de PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Configuration de la base de données PostgreSQL pour SonarQube
echo "📦 Configuration PostgreSQL..."
sudo -u postgres psql -c "CREATE USER sonar WITH PASSWORD 'monpassword';"
sudo -u postgres psql -c "CREATE DATABASE sonarqube OWNER sonar;"

# Vérifier que PostgreSQL fonctionne correctement
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Installation de unzip si ce n’est pas déjà fait
sudo apt install unzip -y

# Création de l'utilisateur SonarQube s'il n'existe pas
if id "sonar" &>/dev/null; then
    echo "✅ L'utilisateur 'sonar' existe déjà."
else
    sudo useradd -m -d /opt/sonarqube -s /bin/bash sonar
    echo "🔑 Définissez un mot de passe pour l'utilisateur sonar :"
    sudo passwd sonar
fi

# Téléchargement de SonarQube
echo "📥 Téléchargement de SonarQube..."
cd /opt
if [ ! -f sonarqube-25.4.0.105899.zip ]; then
    sudo wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-25.4.0.105899.zip
fi

# Extraction et configuration des fichiers
echo "📂 Extraction de SonarQube..."
sudo unzip -o sonarqube-25.4.0.105899.zip
sudo rm -rf /opt/sonarqube
sudo mv sonarqube-25.4.0.105899 sonarqube
sudo chown -R sonar:sonar /opt/sonarqube

# Configuration de SonarQube pour utiliser PostgreSQL
echo "⚙ Configuration de SonarQube pour PostgreSQL..."
sudo sed -i 's/#sonar.jdbc.username=/sonar.jdbc.username=sonar/' /opt/sonarqube/conf/sonar.properties
sudo sed -i 's/#sonar.jdbc.password=/sonar.jdbc.password=monpassword/' /opt/sonarqube/conf/sonar.properties
sudo sed -i 's/#sonar.jdbc.url=jdbc:h2:tcp:\/\/localhost:9092\/sonar/sonar.jdbc.url=jdbc:postgresql:\/\/localhost\/sonarqube/' /opt/sonarqube/conf/sonar.properties

# Création du service systemd pour SonarQube
echo "🛠 Création du service SonarQube..."
sudo tee /etc/systemd/system/sonarqube.service > /dev/null <<EOF
[Unit]
Description=SonarQube service
After=syslog.target network.target postgresql.service

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

# Activation et démarrage de SonarQube
echo "🚀 Démarrage de SonarQube..."
sudo systemctl daemon-reload
sudo systemctl enable sonarqube
sudo systemctl start sonarqube

# Vérification de l'état du service
echo "📡 Vérification du statut de SonarQube..."
sudo systemctl status sonarqube --no-pager

echo "✅ Installation de SonarQube 25.4.0.105899 avec PostgreSQL terminée !"
echo "🌐 Accédez à : http://localhost:9000 (admin / admin)"
