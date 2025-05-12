#!/bin/bash

echo "🚀 Installation complète de l'application et de la base de données PostgreSQL..."

# 🔹 Mise à jour du système
echo "🔄 Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# 🔹 Installation des dépendances
echo "📦 Installation de Python, PostgreSQL et des outils nécessaires..."
sudo apt install -y python3.11-venv python3-pip libpq-dev postgresql postgresql-contrib

# 🔹 Création de l'environnement virtuel
echo "🛠️ Création de l'environnement Python..."
python3 -m venv /venv
source /venv/bin/activate

# 🔹 Vérification du dossier makeapi
if [ ! -d "/makeapi" ]; then
    echo "❌ Erreur : Le dossier /makeapi n'existe pas. Assurez-vous que votre projet est placé correctement."
    exit 1
fi
cd /makeapi

# 🔹 Installation des dépendances Python
echo "⚙️ Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 🔹 Configuration de PostgreSQL
echo "🐘 Configuration de PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 🔹 Modification de la méthode d'authentification PostgreSQL
echo "🔒 Modification de l'authentification PostgreSQL (peer → md5)..."
sudo sed -i "s/local   all             all             peer/local   all             all             md5/" /etc/postgresql/15/main/pg_hba.conf

# 🔹 Redémarrage PostgreSQL
echo "🔄 Redémarrage du service PostgreSQL..."
sudo systemctl restart postgresql

# 🔹 Vérification et création de l'utilisateur PostgreSQL
echo "📊 Vérification et création de l'utilisateur matthieu..."
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'matthieu') THEN
        CREATE ROLE matthieu WITH LOGIN PASSWORD 'postgres';
    END IF;
END
\$\$;
ALTER ROLE matthieu WITH PASSWORD 'postgres';
EOF

# 🔹 Création de la base de données
echo "📊 Création de la base de données makepi_db..."
sudo -u postgres psql <<EOF
CREATE DATABASE makepi_db OWNER matthieu;
GRANT ALL PRIVILEGES ON DATABASE makepi_db TO matthieu;
ALTER SCHEMA public OWNER TO matthieu;
EOF

# 🔹 Activation de pgcrypto
echo "🔐 Activation de pgcrypto pour le cryptage..."
sudo -u postgres psql -d makepi_db <<EOF
CREATE EXTENSION IF NOT EXISTS pgcrypto;
EOF

# 🔹 Création des tables
echo "📌 Création des tables..."
sudo -u postgres psql -d makepi_db <<EOF
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY NOT NULL,
    nom VARCHAR(32) NOT NULL,
    mail VARCHAR(255) NOT NULL,
    motdepasse TEXT NOT NULL,
    actif SMALLINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS public.messages (
    id SERIAL PRIMARY KEY NOT NULL,
    id_user INTEGER NOT NULL,
    objet VARCHAR(255) NOT NULL,
    messages TEXT NOT NULL,
    statut VARCHAR(1) NOT NULL,
    date_message TIMESTAMP NOT NULL,
    FOREIGN KEY (id_user) REFERENCES users(id)
);
EOF

# 🔹 Accorder les droits complets à l'utilisateur PostgreSQL
echo "🔑 Attribution des permissions à matthieu..."
sudo -u postgres psql -d makepi_db <<EOF
GRANT ALL PRIVILEGES ON DATABASE makepi_db TO matthieu;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO matthieu;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO matthieu;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO matthieu;
ALTER SCHEMA public OWNER TO matthieu;
EOF

# 🔹 Application des migrations Django
echo "⚙️ Application des migrations Django..."
python manage.py makemigrations
python manage.py migrate

# 🔹 Vérification et création du superutilisateur Django
echo "🔐 Vérification et création du superutilisateur Django..."
ADMIN_EXISTS=$(echo "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(username='admin').exists())" | python manage.py shell)

if [ "$ADMIN_EXISTS" == "False" ]; then
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')" | python manage.py shell
    echo "✅ Superutilisateur créé."
else
    echo "ℹ️ L'utilisateur admin existe déjà, pas besoin de le recréer."
fi

# 🔹 Lancement du serveur Django
echo "🌍 Démarrage du serveur Django..."
python manage.py runserver 0.0.0.0:8000 &

echo "✅ Installation terminée avec succès !"
