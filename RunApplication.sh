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

# 🔹 Modification de la méthode d'authentification de PostgreSQL
echo "🔒 Modification de la méthode d'authentification de peer à md5..."
sudo sed -i "s/local   all             all             peer/local   all             all             md5/" /etc/postgresql/15/main/pg_hba.conf

# 🔹 Redémarrage de PostgreSQL pour appliquer les changements
echo "🔄 Redémarrage du service PostgreSQL..."
sudo systemctl restart postgresql
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

# 🔹 Création de la base de données
echo "📊 Création de makepi_db..."
sudo -u postgres psql <<EOF
CREATE DATABASE makepi_db OWNER matthieu;
GRANT ALL PRIVILEGES ON DATABASE makepi_db TO matthieu;
ALTER SCHEMA public OWNER TO matthieu;
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
