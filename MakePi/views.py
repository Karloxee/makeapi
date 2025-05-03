global user_on
user_on=None
global admin_user
admin_user=None
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
import io
import pandas as pd
import scipy 
import os
import csv
import save_data_from_api as sd
import seaborn as sns
import numpy as np
import matplotlib
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import urllib, base64
import requests
import datetime 
import dataManager as DM
from django.shortcuts import redirect

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
        # print("Téléchargement terminé. Fichier enregistré sous le nom :", output_file)
    else:
        pass
        # print("La requête a échoué. Statut code :", response.status_code)
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
    # Si une erreur se produit sur la Q1 & Q2 décommenter l'appel de fonction et lancer l'application pour générer un nouveau fichier.
    # Puis commenter l'appel de ce fonction
    # save_data_from_online()
    if creation_date_today() == False:
        save_data_from_online()

    # chemin_fichier_csv = os.path.join(settings.STATIC_ROOT, 'csv/sanisettes_paris.csv')
    df = pd.read_csv("static/csv/sanisettes_paris.csv",sep=';',header=0)
    df = df.drop('URL_FICHE_EQUIPEMENT', axis=1)
    df = df.drop('geo_shape', axis=1)
    df = df.drop('geo_point_2d', axis=1)
    df = df.drop('STATUT', axis=1)
    df=df.dropna(subset=["ARRONDISSEMENT"])
    df['ACCES_PMR'] = df['ACCES_PMR'].apply(modifier_valeur)
    df['RELAIS_BEBE'] = df['RELAIS_BEBE'].apply(modifier_valeur)
    df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].apply(split_arr, header=False)
    df['HORAIRE'] = df['HORAIRE'].apply(modifier_horaire)

    # Copie de la colonne arrondissement en DataFrame
    # Trie les arrondissements
    df_toilette_arrondissement = pd.DataFrame(df['ARRONDISSEMENT'].sort_values()) 
    df_toilette_arrondissement['ARRONDISSEMENT']=df_toilette_arrondissement['ARRONDISSEMENT'].apply(arr_tostring)

    # compter le nombre de toilettes par arrondissement
    nombre_toilette_arrondissement = df_toilette_arrondissement[df_toilette_arrondissement['ARRONDISSEMENT'] == "18"].shape[0] # attention valeur du  ==
    sns.set_theme(style="darkgrid")
    gt_nb_toilette_by_arrondissement = sns.histplot(data=df_toilette_arrondissement, x="ARRONDISSEMENT", discrete=True,  shrink=.5 ) #shrink = largeur de la colonne

    # affichage de la valeur max en haut de chaque colonne
    gt_nb_toilette_by_arrondissement.bar_label(gt_nb_toilette_by_arrondissement.containers[0], fontsize=10)

    # rotation affichage des x
    plt.xticks(rotation=30)

    plt.title("Nombre de toilettes par arrondissement")
    plt.xlabel("Arrondissements")
    plt.ylabel("Toilettes")
    plt.savefig("static/img/q1.png")
    plt.close()


def graph_question2():
    if creation_date_today() == False:
        save_data_from_online()

    # chemin_fichier_csv = os.path.join(settings.STATIC_ROOT, 'csv/sanisettes_paris.csv')
    df = pd.read_csv("static/csv/sanisettes_paris.csv",sep=';',header=0)
    df = df.drop('URL_FICHE_EQUIPEMENT', axis=1)
    df = df.drop('geo_shape', axis=1)
    df = df.drop('geo_point_2d', axis=1)
    df = df.drop('STATUT', axis=1)

    df['ACCES_PMR'] = df['ACCES_PMR'].apply(modifier_valeur)
    df['RELAIS_BEBE'] = df['RELAIS_BEBE'].apply(modifier_valeur)
    df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].apply(split_arr)
    df['HORAIRE'] = df['HORAIRE'].apply(modifier_horaire)
        
    # Copie de la colonne arrondissement en DataFrame
    # Trie les arrondissements
    df_toilette_arrondissement = pd.DataFrame(df['ARRONDISSEMENT'].sort_values()) 
    df_toilette_arrondissement['ARRONDISSEMENT']=df_toilette_arrondissement['ARRONDISSEMENT'].apply(arr_tostring)

    sns.set_theme(style="darkgrid")
    plt.subplots(figsize=(12,8))
    df_type_arrondissement= df.groupby(['TYPE', 'ARRONDISSEMENT']).size().reset_index(name='COUNT') # group by type and arrondissement
    gt_type_by_arrondissement=sns.barplot(data=df_type_arrondissement, x='ARRONDISSEMENT', y='COUNT', hue='TYPE',width=1) # hue:legend, si N width trop grand,trop de temps 
    # pour presenter toutes les valeurs de bar chart
    for containers in gt_type_by_arrondissement.containers:
        gt_type_by_arrondissement.bar_label(containers, fontsize=9) 
    plt.title("Types des Toilettes par arrondissement")
    plt.xlabel("Arrondissement")
    plt.xticks(rotation=30)
    plt.ylabel("Nombre de Toilettes") 
    plt.savefig("static/img/q2.png")
    plt.close()


def graph_question3():
    if creation_date_today() == False:
        save_data_from_online()

    # chemin_fichier_csv = os.path.join(settings.STATIC_ROOT, 'csv/sanisettes_paris.csv')
    df = pd.read_csv("static/csv/sanisettes_paris.csv",sep=';',header=0)
    df = df.drop('URL_FICHE_EQUIPEMENT', axis=1)
    df = df.drop('geo_shape', axis=1)
    df = df.drop('geo_point_2d', axis=1)
    df = df.drop('STATUT', axis=1)

    df['ACCES_PMR'] = df['ACCES_PMR'].apply(modifier_valeur)
    df['RELAIS_BEBE'] = df['RELAIS_BEBE'].apply(modifier_valeur)
    df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].apply(split_arr)
    df['HORAIRE'] = df['HORAIRE'].apply(modifier_horaire)

    # Copie de la colonne arrondissement en DataFrame
    # Trie les arrondissements
    df_toilette_arrondissement = pd.DataFrame(df['ARRONDISSEMENT'].sort_values()) 
    df_toilette_arrondissement['ARRONDISSEMENT']=df_toilette_arrondissement['ARRONDISSEMENT'].apply(arr_tostring)

    pourcentage_AccesPMR = (df['ACCES_PMR'] == 1).mean() * 100

    nbr_acc=(df['ACCES_PMR'] == 1).value_counts()
    comptages = nbr_acc.values.tolist()
    labels = [f'Accès PMR: {comptages[0]}', f'Pas d\'accès PMR: {comptages[1]}']
    sizes = [pourcentage_AccesPMR, 100 - pourcentage_AccesPMR]

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Pourcentage de toilettes ayant accès PMR')
    plt.savefig("static/img/q3.png")
    plt.close()

def toindex(request):
    return HttpResponsePermanentRedirect(reverse('index'))

def index(request):
    return render(request,'index.html')

def generic(request):
    return render(request,'generic.html')

def question1(request):
    # graph_question1()
    return render(request, 'question1.html')

def question2(request):
    # graph_question2()
    return render(request, 'question2.html')

def question3(request):
    # graph_question3()
    return render(request, 'question3.html')

def map(request):
    return render(request, 'map.html')

def inscription(request):
    return render(request, 'inscription.html')

def get_value(row, column_name):
    return getattr(row, column_name)

def display(request):
    df = pd.read_csv("static/csv/sanisettes_paris.csv",sep=';',header=0)
    df = df.drop('URL_FICHE_EQUIPEMENT', axis=1)
    df = df.drop('geo_shape', axis=1)
    df = df.drop('geo_point_2d', axis=1)
    df = df.drop('STATUT', axis=1)
    custom_data = []
    for _, row in df.iterrows():
        custom_data.append({'TYPE': row['TYPE'], 'ARRONDISSEMENT': row['ARRONDISSEMENT']})
    # Passer les données personnalisées au contexte de rendu
    return render(request, 'displaydataframe.html', {'data': custom_data})


def contact(request):
    if 'username' not in request.session:
        return redirect( '../seconnecter/')
    else:
        message=f"Bienvenue {request.session['username']}"
        return render(request, 'contact.html', {"message": message})  

 



def desactiver_user(request,id_user):
    try:
        dataBase =DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        # id_user=request.GET.get("id_user")
        requete=f"update  users set actif=0 where  id ={id_user}"
        if dataBase.Execute_requette(requete)==True:
            dataBase.closeConnexion()
            return redirect("administration")
        else:
            dataBase.closeConnexion()
            message = "Un problème est survenu veuillez réessayer!!"
            return render(request,"admin.html", {"message": message})
    except Exception as e:
        return render(request,"admin.html", {"message": e})


def activer_user(request,id_user):
    try:
        dataBase =DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        #id_user=request.GET.get("id_user")
        requete=f"update  users set actif=1 where id ={id_user}"
        if dataBase.Execute_requette(requete)==True:
            dataBase.closeConnexion()
            return redirect("administration")
        else:
            dataBase.closeConnexion()
            message = "Un problème est survenu veuillez réessayer!!"
            return render(request,"admin.html", {"message": message})
    except Exception as e:
        return render(request,"admin.html", {"message": e})


def delete_user(request,id_user):
    try:
        dataBase=DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        #id_user=request.GET.get("id_user")
        requette=f"delete from users where id ={id_user}"
        if dataBase.Execute_requette(requette)==True:
            dataBase.closeConnexion()
            return redirect("administration")
        else:
            dataBase.closeConnexion()
            message = "Un problème est survenu veuillez réessayer!!"
            return render(request,"admin.html", {"message": message})
    except Exception as e:
        return render(request,"admin.html", {"message": e})


def sinscrire(request):
    try:
        dataBase=DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        nn=request.POST.get("nom")
        nom=nn.replace("'", "''")
        mail=request.POST.get("mail")
        motdepasse=request.POST.get("motdepasse")
        requete=f"insert into users (nom,mail,motdepasse,actif) values('{nom}','{mail}',encode(digest('{motdepasse}', 'sha256'), 'hex'),1)"
        
        if dataBase.insertInto(requete)==True:
            dataBase.closeConnexion()
            global user_on
            user_on=Utilisateur(nom,mail)
            return render(request,"succes.html")
        else:
            dataBase.closeConnexion()
            message = "Un problème est survenu veuillez réessayer!!"
            return render(request,"inscription.html", {"message": message})
    except Exception as e:
        return render(request,"inscription.html", {"message": e})


def envoyer_msg(request):
    try:
        dataBase =DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        objet=request.POST.get("objetmessage").replace("'","''")
        msg=request.POST.get("texto_message").replace("'","''")
        requette=f"insert into messages (objet,messages,statut,date_message,id_user) values('{objet}','{msg}','n',now(),{request.session['id_user']})"
        print(requette)
        if dataBase.insertInto(requette)==True:
            dataBase.closeConnexion()
            message = "Message envoyé avec succès"
            return render(request,"contact.html", {"message": message})
        else:
            dataBase.closeConnexion()
            message = "Un problème est survenu veuillez réessayer!!"
            return render(request,"contact.html", {"message": message})
    except Exception as e:
        return render(request,"contact.html", {"message": e})
    
    
def seconnecter(request):
        try:
            if request.method == 'POST':
                    print(1)
        # Check if the form has been submitted
                    if 'mail' in request.POST and 'motdepasse' in request.POST:
                       
                        dataBase =DM.PostgreSQL('makepi_db')
                      
                        dataBase.setConnexion()
                      
                        mail=request.POST.get("mail").replace("'","''")
                     
                        motdepasse=request.POST.get("motdepasse")
                        requette=f"select count(*) from  users where    mail='{mail}' and motdepasse=encode(digest('{motdepasse}', 'sha256'), 'hex') and actif=1"
                        
                        retour_requete=dataBase.select_user(requette)
                        if retour_requete!=None:
                            if retour_requete!=0:
                                
                                requette=f"select nom from  users where  mail='{mail}' and motdepasse=encode(digest('{motdepasse}', 'sha256'), 'hex') and actif=1"
                                
                                nom=dataBase.select_nameOfuser(requette)
                                username = nom
                                requette=f"select id from  users where  mail='{mail}'"
                                
                                id=dataBase.select_IdOfuser(requette)
                                request.session['id_user'] = id 
                                if nom!=None:
                                    request.session['username'] = username
                                    global user_on
                                    user_on=Utilisateur(nom,mail)
                                    message=f"Bienvenue {nom}"
                                else:
                                    if mail is None:
                                        message = ""
                                    else:
                                        message = "Un problème est survenu veuillez réessayer!!"
                                        
                                    dataBase.closeConnexion()
                                    return render(request,"login.html", {"message": message})
                                dataBase.closeConnexion()

                                return render(request,"contact.html", {"message": message})
                            else:
                                dataBase.closeConnexion()
                                message = "le nom d'utilisateur ou le mot de passe est incorrecte!"
                                return render(request,"login.html", {"message": message}) 
                        else:
                            dataBase.closeConnexion()
                            message = "Vous n'avez pas un compte, veuillez vous inscrire!!"
                            return render(request,"login.html", {"message": message})
                    else:
                          return render(request,"login.html")
            else:
                 return render(request,"login.html")
        except Exception as e:
                print("here")
                return render(request,"login.html", {"message": e})
def admin(request):
    dataBase=DM.PostgreSQL('makepi_db')
    dataBase.setConnexion()
    dataSet=dataBase.selectAll('users')
    dataBase.closeConnexion()
    return render(request,"admin.html", {'dataList':dataSet})


from django.conf import settings

def admin(request):
    if request.method == 'POST':
        if request.POST:
            global admin_user
            mail=request.POST.get("mail")
            motdepass=request.POST.get("motdepasse")
            motdepasse=f"XDEF?TSDFBG!JR%!TR{motdepass}GRPTYSQDERD19SFRET"

            if  mail == settings.LOGIN and motdepasse == settings.ADMIN_PASS :
                admin_user=Utilisateur("Mr l'administeur","admin@greta.com")
                request.session['useradmin']=admin_user.nom
                dataBase =DM.PostgreSQL('makepi_db')
                dataBase.setConnexion()
                dataSet = dataBase.selectAll('users')
                dataBase.closeConnexion()
                message=admin_user.nom
                return render(request,"admin.html", {'dataList':dataSet, "message": message})
            else:
                message="Login ou mot de passe incorrecte!!"
                return render(request,"admin_login.html", {"message": message})
    elif 'useradmin'  in request.session:
        dataBase =DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        dataSet = dataBase.selectAll('users')
        dataBase.closeConnexion()
        message=request.session['useradmin']
        return render(request,"admin.html", {'dataList':dataSet, "message": message})
    else:
        return render(request,"admin_login.html")


def messages(request):
    if 'useradmin'  in request.session:
        dataBase =DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        dataSet = dataBase.selectAllmsg()
        dataBase.closeConnexion()
        message="Mr l'administeur"
        return render(request,"messages.html", {'dataList':dataSet, "message": message})
    else:
        return render(request,"admin_login.html")


def lire_message(request,id_msg):
    if 'useradmin'  in request.session:
        dataBase =DM.PostgreSQL('makepi_db')
        dataBase.setConnexion()
        dataSet = dataBase.selectmsg(id_msg)
        dataBase.closeConnexion()
        message="Mr l'administeur"
        return render(request,"details_message.html", {'dataList':dataSet, "message": message})
    else:
        return render(request,"admin_login.html")


def logout_admin(request) :
    global admin_user
    admin_user=None
    if 'useradmin' in request.session:
        del request.session['useradmin']
    if 'id_user' in request.session:
        del request.session['id_user']
    return redirect("administration")     

def logout(request):
    if 'username' in request.session:
        del request.session['username']
    global user_on
    user_on=None
    return redirect("http://127.0.0.1:8000/")

class Utilisateur():

    def __init__(self,nom,mail):
        self.nom=nom
        self.mail=mail

from django.http import JsonResponse
from MakePi.models import Toilette

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