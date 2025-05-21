import os
import datetime
import requests
import urllib, base64
import csv
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import scipy
import save_data_from_api as sd
import dataManager as DM

from django.http import HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from prometheus_client import Gauge, Counter, generate_latest
from MakePi.models import User as Utilisateur, Toilette
from django.conf import settings

USER_COUNT_GAUGE = Gauge('user_registrations_current', "Nombre actuel d'utilisateurs inscrits")

def get_user_count(request):
    """Récupère le nombre d'utilisateurs inscrits et met à jour la métrique Prometheus"""
    try:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        requete = "SELECT COUNT(*) FROM users"
        result = dataBase.select_user(requete)
        dataBase.closeConnexion()

        # Mise à jour de la métrique Prometheus
        USER_COUNT_GAUGE.set(result)

        return JsonResponse({"user_count": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def update_user_count():
    """Met à jour la métrique Prometheus avec uniquement les utilisateurs actifs"""
    try:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        requete = "SELECT COUNT(*) FROM users WHERE actif=1"  # Comptabilise uniquement les utilisateurs actifs
        result = dataBase.select_user(requete)
        dataBase.closeConnexion()

        USER_COUNT_GAUGE.set(result)  # Met à jour la métrique avec les utilisateurs actifs
    except Exception as e:
        print(f"Erreur lors de la mise à jour de user_registrations_current: {e}")
update_user_count()


def save_data_from_online():
    print("debut")
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/sanisettesparis/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    output_file = "static/csv/sanisettes_paris.csv"
    response = requests.get(url)

    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
    print("fin")

def creation_date_today():
    file_path = "static/csv/sanisettes_paris.csv"
    creation_time = os.path.getctime(file_path)
    creation_datetime = datetime.datetime.fromtimestamp(creation_time)
    today_date = datetime.datetime.now().date()
    
    return creation_datetime.date() == today_date

def modifier_valeur(valeur):
    if pd.isna(valeur):
        return -1
    elif valeur == "Oui":
        return 1
    else:
        return 0

def modifier_horaire(valeur):
    if pd.isna(valeur):
        return -1
    elif valeur == "Voir fiche équipement":
        return "Non mentionné"
    else:
        return valeur

def split_arr(valeur):
    return int(str(valeur)[-2:])

def arr_tostring(valeur):
    return str(valeur)

def graph_question1():
    if not creation_date_today():
        save_data_from_online()

    df = pd.read_csv("static/csv/sanisettes_paris.csv", sep=';', header=0)
    df = df.drop(columns=['URL_FICHE_EQUIPEMENT', 'geo_shape', 'geo_point_2d', 'STATUT'], errors='ignore')
    df.dropna(subset=["ARRONDISSEMENT"], inplace=True)
    df['ACCES_PMR'] = df['ACCES_PMR'].apply(modifier_valeur)
    df['RELAIS_BEBE'] = df['RELAIS_BEBE'].apply(modifier_valeur)
    df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].apply(split_arr)
    df['HORAIRE'] = df['HORAIRE'].apply(modifier_horaire)

    df_toilette_arrondissement = pd.DataFrame(df['ARRONDISSEMENT'].sort_values()) 
    df_toilette_arrondissement['ARRONDISSEMENT'] = df_toilette_arrondissement['ARRONDISSEMENT'].apply(arr_tostring)

    sns.set_theme(style="darkgrid")
    gt_nb_toilette_by_arrondissement = sns.histplot(data=df_toilette_arrondissement, x="ARRONDISSEMENT", discrete=True, shrink=.5)
    gt_nb_toilette_by_arrondissement.bar_label(gt_nb_toilette_by_arrondissement.containers[0], fontsize=10)
    plt.xticks(rotation=30)
    plt.title("Nombre de toilettes par arrondissement")
    plt.xlabel("Arrondissements")
    plt.ylabel("Toilettes")
    plt.savefig("static/img/q1.png")
    plt.close()

def graph_question2():
    if not creation_date_today():
        save_data_from_online()

    df = pd.read_csv("static/csv/sanisettes_paris.csv", sep=';', header=0)
    df = df.drop(columns=['URL_FICHE_EQUIPEMENT', 'geo_shape', 'geo_point_2d', 'STATUT'], errors='ignore')
    df['ACCES_PMR'] = df['ACCES_PMR'].apply(modifier_valeur)
    df['RELAIS_BEBE'] = df['RELAIS_BEBE'].apply(modifier_valeur)
    df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].apply(split_arr)
    df['HORAIRE'] = df['HORAIRE'].apply(modifier_horaire)

    df_type_arrondissement = df.groupby(['TYPE', 'ARRONDISSEMENT']).size().reset_index(name='COUNT')
    sns.set_theme(style="darkgrid")
    plt.subplots(figsize=(12,8))
    gt_type_by_arrondissement = sns.barplot(data=df_type_arrondissement, x='ARRONDISSEMENT', y='COUNT', hue='TYPE', width=1)
    
    for containers in gt_type_by_arrondissement.containers:
        gt_type_by_arrondissement.bar_label(containers, fontsize=9)
    plt.title("Types des Toilettes par arrondissement")
    plt.xlabel("Arrondissement")
    plt.xticks(rotation=30)
    plt.ylabel("Nombre de Toilettes")
    plt.savefig("static/img/q2.png")
    plt.close()

def graph_question3():
    if not creation_date_today():
        save_data_from_online()

    df = pd.read_csv("static/csv/sanisettes_paris.csv", sep=';', header=0)
    df = df.drop(columns=['URL_FICHE_EQUIPEMENT', 'geo_shape', 'geo_point_2d', 'STATUT'], errors='ignore')
    df['ACCES_PMR'] = df['ACCES_PMR'].apply(modifier_valeur)
    df['RELAIS_BEBE'] = df['RELAIS_BEBE'].apply(modifier_valeur)
    df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].apply(split_arr)
    df['HORAIRE'] = df['HORAIRE'].apply(modifier_horaire)

    pourcentage_AccesPMR = (df['ACCES_PMR'] == 1).mean() * 100
    nbr_acc = (df['ACCES_PMR'] == 1).value_counts()
    comptages = nbr_acc.values.tolist()
    labels = [f'Accès PMR: {comptages[0]}', f'Pas d\'accès PMR: {comptages[1]}']
    sizes = [pourcentage_AccesPMR, 100 - pourcentage_AccesPMR]

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Pourcentage de toilettes ayant accès PMR')
    plt.savefig("static/img/q3.png")
    plt.close()

def toindex(request):
    return HttpResponsePermanentRedirect(reverse('index'))

def index(request):
    return render(request, 'index.html')

def generic(request):
    return render(request, 'generic.html')

def question1(request):
    return render(request, 'question1.html')

def question2(request):
    return render(request, 'question2.html')

def question3(request):
    return render(request, 'question3.html')

def map(request):
    return render(request, 'map.html')

def inscription(request):
    return render(request, 'inscription.html')

def get_value(row, column_name):
    return getattr(row, column_name)

def display(request):
    df = pd.read_csv("static/csv/sanisettes_paris.csv", sep=';', header=0)
    df = df.drop(columns=['URL_FICHE_EQUIPEMENT', 'geo_shape', 'geo_point_2d', 'STATUT'], errors='ignore')

    custom_data = [{'TYPE': row['TYPE'], 'ARRONDISSEMENT': row['ARRONDISSEMENT']} for _, row in df.iterrows()]
    return render(request, 'displaydataframe.html', {'data': custom_data})

def contact(request):
    if 'username' not in request.session:
        return redirect('../seconnecter/')
    else:
        message = f"Bienvenue {request.session['username']}"
        return render(request, 'contact.html', {"message": message})

def desactiver_user(request, id_user):
    try:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        requete = f"UPDATE users SET actif=0 WHERE id={id_user}"
        if dataBase.Execute_requette(requete):
            update_user_count() 
            dataBase.closeConnexion()
            return redirect("administration")
        else:
            dataBase.closeConnexion()
            return render(request, "admin.html", {"message": "Un problème est survenu, veuillez réessayer !!"})
    except Exception as e:
        return render(request, "admin.html", {"message": str(e)})

def activer_user(request, id_user):
    try:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        requete = f"UPDATE users SET actif=1 WHERE id={id_user}"
        if dataBase.Execute_requette(requete):
            update_user_count() 
            dataBase.closeConnexion()
            return redirect("administration")
        else:
            dataBase.closeConnexion()
            return render(request, "admin.html", {"message": "Un problème est survenu, veuillez réessayer !!"})
    except Exception as e:
        return render(request, "admin.html", {"message": str(e)})

def delete_user(request, id_user):
    try:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        requete = f"DELETE FROM users WHERE id={id_user}"
        if dataBase.Execute_requette(requete):
            update_user_count() 
            dataBase.closeConnexion()
            return redirect("administration")
        else:
            dataBase.closeConnexion()
            return render(request, "admin.html", {"message": "Un problème est survenu, veuillez réessayer !!"})
    except Exception as e:
        return render(request, "admin.html", {"message": str(e)})

def sinscrire(request):
    try:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        nn = request.POST.get("nom")
        nom = nn.replace("'", "''")
        mail = request.POST.get("mail")
        motdepasse = request.POST.get("motdepasse")
        requete = f"INSERT INTO users (nom, mail, motdepasse, actif) VALUES ('{nom}', '{mail}', encode(digest('{motdepasse}', 'sha256'), 'hex'), 1)"

        if dataBase.insertInto(requete):
            dataBase.closeConnexion()
            update_user_count() 
            global user_on
            user_on = Utilisateur(nom, mail)
            return render(request, "succes.html")
        else:
            dataBase.closeConnexion()
            return render(request, "inscription.html", {"message": "Un problème est survenu, veuillez réessayer !!"})
    except Exception as e:
        return render(request, "inscription.html", {"message": str(e)})


def envoyer_msg(request):
    try:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        objet = request.POST.get("objetmessage").replace("'", "''")
        msg = request.POST.get("texto_message").replace("'", "''")
        requete = f"INSERT INTO messages (objet, messages, statut, date_message, id_user) VALUES ('{objet}', '{msg}', 'n', now(), {request.session['id_user']})"

        if dataBase.insertInto(requete):
            dataBase.closeConnexion()
            return render(request, "contact.html", {"message": "Message envoyé avec succès"})
        else:
            dataBase.closeConnexion()
            return render(request, "contact.html", {"message": "Un problème est survenu, veuillez réessayer !!"})
    except Exception as e:
        return render(request, "contact.html", {"message": str(e)})

def seconnecter(request):
    try:
        if request.method == 'POST' and 'mail' in request.POST and 'motdepasse' in request.POST:
            dataBase = DM.PostgreSQL('makepi_db')
            dataBase.setConnexion()

            mail = request.POST.get("mail").replace("'", "''")
            motdepasse = request.POST.get("motdepasse")
            requete = f"SELECT COUNT(*) FROM users WHERE mail='{mail}' AND motdepasse=encode(digest('{motdepasse}', 'sha256'), 'hex') AND actif=1"

            retour_requete = dataBase.select_user(requete)
            if retour_requete and retour_requete != 0:
                nom = dataBase.select_nameOfuser(f"SELECT nom FROM users WHERE mail='{mail}'")
                id_user = dataBase.select_IdOfuser(f"SELECT id FROM users WHERE mail='{mail}'")
                request.session['id_user'] = id_user
                request.session['username'] = nom

                global user_on
                user_on = Utilisateur(nom, mail)

                dataBase.closeConnexion()
                return render(request, "contact.html", {"message": f"Bienvenue {nom}"})
            else:
                dataBase.closeConnexion()
                return render(request, "login.html", {"message": "Le nom d'utilisateur ou le mot de passe est incorrecte!"})
        return render(request, "login.html")
    except Exception as e:
        return render(request, "login.html", {"message": str(e)})

def admin(request):
    if request.method == 'POST':
        global admin_user
        mail = request.POST.get("mail")
        motdepass = request.POST.get("motdepasse")
        motdepasse = f"XDEF?TSDFBG!JR%!TR{motdepass}GRPTYSQDERD19SFRET"

        if mail == settings.LOGIN and motdepasse == settings.ADMIN_PASS:
            admin_user = Utilisateur("Mr l'administrateur", "admin@greta.com")
            request.session['useradmin'] = admin_user.nom
            dataBase = DM.PostgreSQL('makepi_db')
            dataBase.setConnexion()
            dataSet = dataBase.selectAll('users')
            dataBase.closeConnexion()
            return render(request, "admin.html", {'dataList': dataSet, "message": admin_user.nom})
        else:
            return render(request, "admin_login.html", {"message": "Login ou mot de passe incorrecte !!"})
    elif 'useradmin' in request.session:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        dataSet = dataBase.selectAll('users')
        dataBase.closeConnexion()
        return render(request, "admin.html", {'dataList': dataSet, "message": request.session['useradmin']})
    else:
        return render(request, "admin_login.html")

def messages(request):
    if 'useradmin' in request.session:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        dataSet = dataBase.selectAllmsg()
        dataBase.closeConnexion()
        return render(request, "messages.html", {'dataList': dataSet, "message": "Mr l'administrateur"})
    else:
        return render(request, "admin_login.html")

def lire_message(request, id_msg):
    if 'useradmin' in request.session:
        dataBase = DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        dataSet = dataBase.selectmsg(id_msg)
        dataBase.closeConnexion()
        return render(request, "details_message.html", {'dataList': dataSet, "message": "Mr l'administrateur"})
    else:
        return render(request, "admin_login.html")

def logout_admin(request):
    global admin_user
    admin_user = None
    request.session.pop('useradmin', None)
    request.session.pop('id_user', None)
    return redirect("administration")

def logout(request):
    request.session.pop('username', None)
    global user_on
    user_on = None
    return redirect("http://127.0.0.1:8000/")

class Utilisateur:
    def __init__(self, nom, mail):
        self.nom = nom
        self.mail = mail

def toilettes_api(request):
    pmr = request.GET.get('pmr')
    bebe = request.GET.get('bebe')
    arr = request.GET.get('arr')

    toilettes = Toilette.objects.all()
    if pmr == '1':
        toilettes = toilettes.filter(acces_pmr=True)
    if bebe == '1':
        toilettes = toilettes.filter(relais_bebe=True)
    if arr:
        toilettes = toilettes.filter(arrondissement=f"750{arr.zfill(2)}")

    data = [{
        'type': t.type,
        'adresse': t.adresse,
        'pmr': t.acces_pmr,
        'bebe': t.relais_bebe,
        'lat': t.latitude,
        'lng': t.longitude
    } for t in toilettes]

    return JsonResponse(data, safe=False)