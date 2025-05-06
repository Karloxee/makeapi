#!/bin/bash

echo "🚀 Début de l'installation de Prometheus 3.3.1 sur Debian..."

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Création d'un utilisateur pour Prometheus
sudo useradd --no-create-home --shell /bin/false prometheus

# Création des dossiers nécessaires
echo "📂 Création des dossiers de configuration..."
sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus

# Téléchargement de Prometheus 3.3.1
PROM_VERSION="3.3.1"
wget https://github.com/prometheus/prometheus/releases/download/v$PROM_VERSION/prometheus-$PROM_VERSION.linux-amd64.tar.gz

# Extraction des fichiers directement dans la racine /
echo "📂 Extraction de Prometheus dans la racine..."
sudo tar xvf prometheus-$PROM_VERSION.linux-amd64.tar.gz -C /

# Déplacement des fichiers binaires vers /usr/local/bin
echo "🚀 Configuration des binaires Prometheus..."
sudo mv /prometheus-$PROM_VERSION.linux-amd64/prometheus /usr/local/bin/
sudo mv /prometheus-$PROM_VERSION.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus /usr/local/bin/promtool

# Déplacement des fichiers de configuration vers /etc/prometheus
echo "🛠 Configuration des fichiers Prometheus..."
sudo mv /prometheus-$PROM_VERSION.linux-amd64/consoles /etc/prometheus/
sudo mv /prometheus-$PROM_VERSION.linux-amd64/console_libraries /etc/prometheus/
sudo mv /prometheus-$PROM_VERSION.linux-amd64/prometheus.yml /etc/prometheus/
sudo chown -R prometheus:prometheus /etc/prometheus

# Vérification et correction si prometheus.yml manque
if [ ! -f /etc/prometheus/prometheus.yml ]; then
    echo "⚠ Le fichier prometheus.yml est manquant, téléchargement du fichier par défaut..."
    sudo wget -O /etc/prometheus/prometheus.yml https://raw.githubusercontent.com/prometheus/prometheus/main/documentation/examples/prometheus.yml
    sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
    sudo chmod 644 /etc/prometheus/prometheus.yml
fi

# Suppression du fichier tar.gz après l'installation
echo "🗑 Suppression du fichier d'installation tar.gz..."
sudo rm -f prometheus-$PROM_VERSION.linux-amd64.tar.gz

# Création du service systemd pour Prometheus
echo "🔧 Création du service Prometheus..."
sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOF
[Unit]
Description=Prometheus Monitoring
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus \
  --web.listen-address=:9090 \
  --web.enable-lifecycle
  
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Activation et démarrage du service Prometheus
echo "🚀 Démarrage de Prometheus..."
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus

# Vérification du statut du service
echo "📡 Vérification du statut Prometheus..."
sudo systemctl status prometheus --no-pager

echo "✅ Installation de Prometheus 3.3.1 terminée avec succès !"
echo "🌐 Accédez à Prometheus via : http://localhost:9090"
