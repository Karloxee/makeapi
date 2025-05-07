#!/bin/bash
#MARCHE UNIQUEMENT SI VOUS AVEZ UN DOSSIER makeapi a la racine de debian sinon adapter !
echo "🚀 Installation de l'application et de la base de données PostgreSQL..."
# 🔹 Mise à jour du système
sudo apt update && sudo apt upgrade -y
# 🔹 Installation des dépendances
echo "📦 Installation de Python et des outils nécessaires..."
sudo apt install -y python3.11-venv python3-pip libpq-dev postgresql postgresql-contrib
# 🔹 Création de l'environnement virtuel à la racine
echo "🛠️ Création de l'environnement Python..."
python3 -m venv /venv
source /venv/bin/activate
# 🔹 Vérification du dossier makeapi
if [ ! -d "/makeapi" ]; then
    echo "❌ Erreur : Le dossier /makeapi n'existe pas. Assurez-vous que votre projet est placé correctement."
    exit 1
fi
cd /makeapi
# 🔹 Installation des dépendances Python depuis makeapi
echo "⚙️ Installation des dépendances..."
pip install --upgrade pip
pip install -r /makeapi/requirements.txt  # 🔹 Mise à jour du chemin
# 🔹 Lancement du serveur Django
echo "🌍 Lancement du serveur Django..."
python manage.py runserver 0.0.0.0:8000 &
# 🔹 Configuration de PostgreSQL
echo "🐘 Configuration de PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 🔹 Définition du mot de passe pour l'utilisateur postgres
echo "🔑 Définition du mot de passe pour l'utilisateur système postgres..."
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# 🔹 Modification des méthodes d'authentification de PostgreSQL
echo "🔒 Modification des méthodes d'authentification de peer à md5..."
# Modifier toutes les méthodes d'authentification locales (peer -> md5)
sudo sed -i '/^local/s/peer/md5/g' /etc/postgresql/15/main/pg_hba.conf
# Vérifier également les connexions host pour localhost
sudo sed -i '/^host.*127.0.0.1/s/ident/md5/g' /etc/postgresql/15/main/pg_hba.conf
sudo sed -i '/^host.*::1/s/ident/md5/g' /etc/postgresql/15/main/pg_hba.conf

# 🔹 Vérification manuelle de la configuration
echo "📋 Affichage de la configuration actuelle pg_hba.conf pour vérification :"
sudo cat /etc/postgresql/15/main/pg_hba.conf | grep -v "^#" | grep -v "^$"

# 🔹 Redémarrage de PostgreSQL pour appliquer les changements
echo "🔄 Redémarrage du service PostgreSQL..."
sudo systemctl restart postgresql
sleep 2  # Attendre que PostgreSQL redémarre complètement
# 🔹 Vérification et création du rôle matthieu
echo "📊 Vérification et création de l'utilisateur matthieu..."
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'matthieu') THEN
        CREATE ROLE matthieu WITH LOGIN PASSWORD 'postgres';
    END IF;
END
\$\$;
EOF

# 🔹 Modification du mot de passe pour matthieu (ajout demandé)
echo "🔐 Définition du mot de passe pour l'utilisateur matthieu..."
sudo -u postgres psql <<EOF
ALTER ROLE matthieu WITH PASSWORD 'postgres';
EOF

# 🔹 Création et configuration de la base de données
echo "📊 Création de makepi_db..."
sudo -u postgres psql <<EOF
CREATE DATABASE makepi_db OWNER matthieu;
GRANT ALL PRIVILEGES ON DATABASE makepi_db TO matthieu;
ALTER SCHEMA public OWNER TO matthieu;
EOF

# Test de connexion avec la nouvelle configuration
echo "🔍 Test de connexion à la base de données avec l'utilisateur matthieu..."
PGPASSWORD=postgres psql -U matthieu -h localhost -d makepi_db -c "SELECT 1 AS connection_test;"

# Ajout de configuration supplémentaire pour PostgreSQL si nécessaire
echo "⚙️ Ajout de configuration supplémentaire pour PostgreSQL..."
sudo -u postgres psql <<EOF
ALTER ROLE matthieu SUPERUSER;
EOF

# 🔹 Vérification et activation de l'extension crypto
echo "🔍 Vérification de l'extension crypto..."
sudo -u postgres psql -d makepi_db <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'crypto') THEN
        CREATE EXTENSION crypto;
    END IF;
END
\$\$;
EOF
# 🔹 Création des tables dans makepi_db
echo "📌 Création des tables..."
sudo -u postgres psql -d makepi_db <<EOF
CREATE TABLE IF NOT EXISTS public.users (
    id serial PRIMARY KEY NOT NULL,
    nom character varying(32) NOT NULL,
    mail character varying(255) NOT NULL,
    motdepasse character varying(255) NOT NULL,
    actif smallint
);
CREATE TABLE IF NOT EXISTS public.messages (
    id serial PRIMARY KEY NOT NULL,
    id_user integer NOT NULL,
    objet character varying(255) NOT NULL,
    messages text NOT NULL,
    statut character varying(1) NOT NULL,
    date_message timestamp NOT NULL,
    FOREIGN KEY (id_user) REFERENCES users(id)
);
EOF
echo "✅ Installation terminée !"
