#!/bin/bash

echo "Installation complète de l'application et de la base de données PostgreSQL..."

# Mise à jour du système
echo " Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
echo "Installation de Python, PostgreSQL et des outils nécessaires..."
sudo apt install -y python3.11-venv python3-pip libpq-dev postgresql postgresql-contrib

# Création de l'environnement virtuel
echo "Création de l'environnement Python..."
python3 -m venv /venv
source /venv/bin/activate

# Vérification du dossier makeapi
if [ ! -d "/makeapi" ]; then
    echo "Erreur : Le dossier /makeapi n'existe pas. Assurez-vous que votre projet est placé correctement."
    exit 1
fi
cd /makeapi

# Installation des dépendances Python
echo "Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configuration de PostgreSQL
echo "Configuration de PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Modification de l'authentification PostgreSQL
echo "Modification de l'authentification PostgreSQL (peer → md5)..."
sudo sed -i "s/local   all             all             peer/local   all             all             md5/" /etc/postgresql/*/main/pg_hba.conf

# Redémarrage PostgreSQL
echo "Redémarrage du service PostgreSQL..."
sudo systemctl restart postgresql

# Vérification et création de l'utilisateur PostgreSQL
echo "Vérification et création de l'utilisateur matthieu..."
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'matthieu') THEN
        CREATE ROLE matthieu WITH LOGIN PASSWORD 'postgres';
    END IF;
END
\$\$;
ALTER ROLE matthieu WITH PASSWORD 'postgres';
GRANT CREATE ON SCHEMA public TO matthieu;
EOF

# Création de la base de données
echo "Création de la base de données makepi_db..."
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS makepi_db;
CREATE DATABASE makepi_db OWNER matthieu;
GRANT ALL PRIVILEGES ON DATABASE makepi_db TO matthieu;
ALTER SCHEMA public OWNER TO matthieu;
EOF

# Activation de pgcrypto
echo "Activation de pgcrypto pour le cryptage..."
sudo -u postgres psql -d makepi_db <<EOF
CREATE EXTENSION IF NOT EXISTS pgcrypto;
EOF

# Création des tables
echo "Création des tables..."
sudo -u postgres psql -d makepi_db <<EOF
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY NOT NULL,
    nom VARCHAR(32) NOT NULL,
    mail VARCHAR(255) NOT NULL,
    motdepasse TEXT NOT NULL,
    actif SMALLINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY NOT NULL,
    id_user INTEGER NOT NULL,
    objet VARCHAR(255) NOT NULL,
    messages TEXT NOT NULL,
    statut VARCHAR(1) NOT NULL,
    date_message TIMESTAMP NOT NULL,
    FOREIGN KEY (id_user) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS toilettes (
    id SERIAL PRIMARY KEY NOT NULL,
    type VARCHAR(100),
    adresse TEXT,
    arrondissement VARCHAR(5),
    horaires VARCHAR(255),
    acces_pmr BOOLEAN DEFAULT FALSE,
    relais_bebe BOOLEAN DEFAULT FALSE,
    latitude FLOAT,
    longitude FLOAT
);
EOF

# Attribution des permissions à matthieu
echo "Configuration des permissions..."
sudo -u postgres psql -d makepi_db <<EOF
GRANT ALL PRIVILEGES ON DATABASE makepi_db TO matthieu;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO matthieu;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO matthieu;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO matthieu;
ALTER SCHEMA public OWNER TO matthieu;
EOF

# Application des migrations Django
echo "Application des migrations Django..."
python manage.py makemigrations MakePi
python manage.py migrate --fake-initial

# Correction des erreurs de migration
echo "Correction des migrations Django..."
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate sessions
python manage.py migrate --fake MakePi

# Vérification et création du superutilisateur Django (matthieu)
echo "Vérification et création du superutilisateur Django..."
ADMIN_EXISTS=$(echo "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(username='matthieu').exists())" | python manage.py shell)

if [ "$ADMIN_EXISTS" == "False" ]; then
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('matthieu', 'matthieu@example.com', 'postgres')" | python manage.py shell
    echo "Superutilisateur matthieu créé."
else
    echo "L'utilisateur matthieu existe déjà, pas besoin de le recréer."
fi

# Importation des données de toilettes
echo "Importation des données de toilettes..."
python manage.py import_toilettes

# Vérification que le port 8000 est uniquement utilisé par Django
echo "Vérification de l'utilisation du port 8000 par Django..."
DJANGO_PID=$(pgrep -f "manage.py runserver")
if [ -n "$DJANGO_PID" ]; then
    echo "Un processus Django est déjà en cours d'exécution sur le port 8000. Arrêt du processus..."
    kill -9 $DJANGO_PID
fi

# Lancement du serveur Django
echo "Démarrage du serveur Django sur le port 8000..."
python manage.py runserver 0.0.0.0:8000 &

echo "Installation terminée avec succès !"
