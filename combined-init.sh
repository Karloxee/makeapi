
#!/bin/bash
set -e

##############################
# 🚀 INSTALLATION PROMETHEUS #
##############################

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

# Extraction des fichiers
echo "📂 Extraction de Prometheus..."
tar xvf prometheus-$PROM_VERSION.linux-amd64.tar.gz

# Déplacement des fichiers binaires
echo "🚀 Configuration des binaires Prometheus..."
sudo mv prometheus-$PROM_VERSION.linux-amd64/prometheus /usr/local/bin/
sudo mv prometheus-$PROM_VERSION.linux-amd64/promtool /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/prometheus /usr/local/bin/promtool

# Déplacement de la configuration
echo "🛠 Configuration des fichiers Prometheus..."
sudo mv prometheus-$PROM_VERSION.linux-amd64/consoles /etc/prometheus/
sudo mv prometheus-$PROM_VERSION.linux-amd64/console_libraries /etc/prometheus/
sudo mv prometheus-$PROM_VERSION.linux-amd64/prometheus.yml /etc/prometheus/
sudo chown -R prometheus:prometheus /etc/prometheus

# Vérification du fichier prometheus.yml
if [ ! -f /etc/prometheus/prometheus.yml ]; then
    echo "⚠ Fichier prometheus.yml manquant. Téléchargement..."
    sudo wget -O /etc/prometheus/prometheus.yml https://raw.githubusercontent.com/prometheus/prometheus/main/documentation/examples/prometheus.yml
    sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
    sudo chmod 644 /etc/prometheus/prometheus.yml
fi

# Nettoyage
sudo rm -f prometheus-$PROM_VERSION.linux-amd64.tar.gz
rm -rf prometheus-$PROM_VERSION.linux-amd64

# Création du service Prometheus
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
ExecStart=/usr/local/bin/prometheus \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/var/lib/prometheus \\
  --web.listen-address=:9090 \\
  --web.enable-lifecycle

Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Démarrage du service
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus

# Vérification
sudo systemctl status prometheus --no-pager

echo "✅ Prometheus installé avec succès !"

###########################
# 📊 INSTALLATION GRAFANA #
###########################

echo "🚀 Début de l'installation de Grafana sur Debian..."
