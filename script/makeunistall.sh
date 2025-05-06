#!/bin/bash

echo "🚨 Désinstallation de l'application et des services associés..."

# 🔹 Désactivation de l'environnement virtuel
echo "🛠️ Désactivation et suppression de l'environnement Python..."
deactivate || echo "L'environnement virtuel n'était pas actif."
rm -rf /venv

# 🔹 Suppression des dépendances Python
echo "⚙️ Suppression des dépendances Python..."
pip freeze | xargs pip uninstall -y

# 🔹 Arrêt et suppression de la base de données PostgreSQL
echo "🐘 Suppression de la base de données et du rôle utilisateur PostgreSQL..."
sudo systemctl stop postgresql
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS makepi_db;
DROP ROLE IF EXISTS matthieu;
EOF
sudo systemctl disable postgresql

# 🔹 Suppression du répertoire du projet
echo "🗑️ Suppression du répertoire du projet..."
rm -rf /makepipoo

echo "✅ Désinstallation terminée !"
