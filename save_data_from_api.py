import requests
import os
import datetime

 
def save_data_from_online():
    print("debut")
# Lien vers le fichier CSV
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/sanisettesparis/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"

    # Nom du fichier de sortie
    output_file = "static/csv/sanisettes_paris.csv"

    # Effectuer la requête HTTP
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Écrire le contenu de la réponse dans un fichier CSV
        with open(output_file, 'wb') as f:
            f.write(response.content)
        #print("Téléchargement terminé. Fichier enregistré sous le nom :", output_file)
    else:
        pass
        #print("La requête a échoué. Statut code :", response.status_code)
    print("fin")
def creation_date_today():
    file_path = "static/csv/sanisettes_paris.csv"
    print(file_path)
    # Obtient la date de création du fichier
    creation_time = os.path.getctime(file_path)
    
    # Convertit le temps de création en objet de date et heure
    creation_datetime = datetime.datetime.fromtimestamp(creation_time)
    
    # Obtient la date d'aujourd'hui
    today_date = datetime.datetime.now().date()
    
    # Vérifie si la date de création correspond à la date d'aujourd'hui
    if creation_datetime.date() == today_date:
        return True
    else:
        return False


