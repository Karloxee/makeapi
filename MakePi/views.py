# MakePi/views.py
import os
import datetime
import pandas as pd
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
import dataManager as DM
from MakePi.models import Toilette

# -- Globals pour session utilisateur/admin
user_on = None
admin_user = None

# -- Chargement unique du CSV des sanisettes (mis à jour via cron)
CSV_PATH = os.path.join(settings.BASE_DIR, 'static', 'csv', 'sanisettes_paris.csv')
_df = pd.read_csv(CSV_PATH, sep=';')  # adapter le séparateur si besoin

# ------------------------------
# Endpoints JSON pour Chart.js
# ------------------------------

def question1_data(request):
    """
    Nombre de sanisettes par arrondissement
    """
    counts = _df['ARRONDISSEMENT'].value_counts().sort_index()
    return JsonResponse({
        'labels': counts.index.astype(str).tolist(),
        'data':   counts.values.tolist()
    })


def question2_data(request):
    """
    Répartition des types de sanisettes par arrondissement
    """
    pivot = _df.pivot_table(
        index='ARRONDISSEMENT',
        columns='TYPE',
        aggfunc='size',
        fill_value=0
    ).sort_index()
    datasets = [
        {'label': col, 'data': pivot[col].tolist()} for col in pivot.columns
    ]
    return JsonResponse({
        'labels':   pivot.index.astype(str).tolist(),
        'datasets': datasets
    })


def question3_data(request):
    """
    Pourcentage d'accès PMR
    Retourne JSON: { labels: [...], data: [...] }
    """
    total    = len(_df)  # int natif
    pmr_yes  = int((_df['ACCES_PMR'].str.upper() == 'OUI').sum())
    pmr_no   = total - pmr_yes

    return JsonResponse({
        'labels': ['Accès PMR', "Pas d'accès PMR"],
        'data':   [pmr_yes, pmr_no]
    })

# ------------------------------
# Vues HTML
# ------------------------------

def question1_view(request):
    return render(request, 'question1.html')


def question2_view(request):
    return render(request, 'question2.html')


def question3_view(request):
    return render(request, 'question3.html')

# ------------------------------
# Autres vues existantes
# ------------------------------

def toindex(request):
    return HttpResponsePermanentRedirect(reverse('index'))


def index(request):
    return render(request, 'index.html')


def generic(request):
    return render(request, 'generic.html')


def map(request):
    return render(request, 'map.html')


def inscription(request):
    return render(request, 'inscription.html')


def display(request):
    """
    Affiche un tableau simplifié TYPE / ARRONDISSEMENT
    """
    df = _df.drop(columns=['URL_FICHE_EQUIPEMENT', 'geo_shape', 'geo_point_2d', 'STATUT'], errors='ignore')
    custom_data = [
        {'TYPE': row.TYPE, 'ARRONDISSEMENT': row.ARRONDISSEMENT}
        for row in df.itertuples()
    ]
    return render(request, 'displaydataframe.html', {'data': custom_data})


def contact(request):
    if 'username' not in request.session:
        return redirect('../seconnecter/')
    message = f"Bienvenue {request.session.get('username')}"
    return render(request, 'contact.html', {"message": message})


def desactiver_user(request, id_user):
    try:
        db = DM.PostgreSQL('makepi_db')
        db.setConnexion()
        q = f"UPDATE users SET actif=0 WHERE id={id_user}"
        success = db.Execute_requette(q)
        db.closeConnexion()
        if success:
            return redirect('administration')
        raise Exception("Échec de la requête")
    except Exception as e:
        return render(request, 'admin.html', {"message": e})


def activer_user(request, id_user):
    try:
        db = DM.PostgreSQL('makepi_db')
        db.setConnexion()
        q = f"UPDATE users SET actif=1 WHERE id={id_user}"
        success = db.Execute_requette(q)
        db.closeConnexion()
        if success:
            return redirect('administration')
        raise Exception("Échec de la requête")
    except Exception as e:
        return render(request, 'admin.html', {"message": e})


def delete_user(request, id_user):
    try:
        db = DM.PostgreSQL('makepi_db')
        db.setConnexion()
        q = f"DELETE FROM users WHERE id={id_user}"
        success = db.Execute_requette(q)
        db.closeConnexion()
        if success:
            return redirect('administration')
        raise Exception("Échec de la requête")
    except Exception as e:
        return render(request, 'admin.html', {"message": e})


def sinscrire(request):
    try:
        db = DM.PostgreSQL('makepi_db')
        db.setConnexion()
        nom = request.POST.get('nom', '').replace("'", "''")
        mail = request.POST.get('mail', '')
        mdp = request.POST.get('motdepasse', '')
        q = (
            "INSERT INTO users (nom,mail,motdepasse,actif) VALUES(" +
            f"'{nom}','{mail}',encode(digest('{mdp}','sha256'),'hex'),1)"
        )
        success = db.insertInto(q)
        db.closeConnexion()
        if success:
            global user_on
            user_on = type('U', (), {'nom': nom, 'mail': mail})()
            return render(request, 'succes.html')
        raise Exception("Échec de l'insertion")
    except Exception as e:
        return render(request, 'inscription.html', {'message': e})


def envoyer_msg(request):
    try:
        db = DM.PostgreSQL('makepi_db')
        db.setConnexion()
        obj = request.POST.get('objetmessage','').replace("'","''")
        msg = request.POST.get('texto_message','').replace("'","''")
        uid = request.session.get('id_user', 0)
        q = (
            "INSERT INTO messages (objet,messages,statut,date_message,id_user) VALUES(" +
            f"'{obj}','{msg}','n',now(),{uid})"
        )
        success = db.insertInto(q)
        db.closeConnexion()
        if success:
            return render(request, 'contact.html', {'message': 'Message envoyé avec succès'})
        raise Exception("Échec de l'insertion")
    except Exception as e:
        return render(request, 'contact.html', {'message': e})


def seconnecter(request):
    try:
        if request.method == 'POST':
            mail = request.POST.get('mail','').replace("'","''")
            mdp = request.POST.get('motdepasse','')
            db = DM.PostgreSQL('makepi_db')
            db.setConnexion()
            q_count = (
                f"SELECT count(*) FROM users WHERE mail='{mail}' " +
                f"AND motdepasse=encode(digest('{mdp}','sha256'),'hex') AND actif=1"
            )
            count = db.select_user(q_count)
            if count and count != 0:
                q_nom = q_count.replace('count(*)','nom')
                nom = db.select_nameOfuser(q_nom)
                q_id = q_count.replace('count(*)','id')
                uid = db.select_IdOfuser(q_id)
                request.session['id_user'] = uid
                request.session['username'] = nom
                db.closeConnexion()
                return render(request, 'contact.html', {'message': f'Bienvenue {nom}'})
            db.closeConnexion()
            return render(request, 'login.html', {'message': 'Identifiants invalides'})
        return render(request, 'login.html')
    except Exception as e:
        return render(request, 'login.html', {'message': e})


def admin(request):
    if request.method == 'POST':
        mail = request.POST.get('mail','')
        mdp = request.POST.get('motdepasse', '')
        mdp_enc = f"XDEF?TSDFBG!JR%!TR{mdp}GRPTYSQDERD19SFRET"
        if mail == settings.LOGIN and mdp_enc == settings.ADMIN_PASS:
            global admin_user
            admin_user = type('A', (), {'nom':'Admin'})()
            request.session['useradmin'] = admin_user.nom
        else:
            return render(request,'admin_login.html',{'message':'Login ou mot de passe incorrect'})
    if 'useradmin' in request.session:
        db = DM.PostgreSQL('makepi_db'); db.setConnexion()
        dataSet = db.selectAll('users'); db.closeConnexion()
        return render(request,'admin.html',{'dataList':dataSet,'message':request.session['useradmin']})
    return render(request,'admin_login.html')


def messages(request):
    if 'useradmin' in request.session:
        db = DM.PostgreSQL('makepi_db'); db.setConnexion()
        dataSet = db.selectAllmsg(); db.closeConnexion()
        return render(request,'messages.html',{'dataList':dataSet,'message':'Admin'})
    return redirect('admin_login')


def lire_message(request, id_msg):
    if 'useradmin' in request.session:
        db = DM.PostgreSQL('makepi_db'); db.setConnexion()
        dataSet = db.selectmsg(id_msg); db.closeConnexion()
        return render(request,'details_message.html',{'dataList':dataSet,'message':'Admin'})
    return redirect('admin_login')


def logout_admin(request):
    global admin_user; admin_user=None
    request.session.pop('useradmin',None)
    return redirect("administration")


def logout(request):
    global user_on; user_on=None
    request.session.pop('username',None)
    return redirect('/')


def toilettes_api(request):
    pmr = request.GET.get('pmr')
    bebe = request.GET.get('bebe')
    arr = request.GET.get('arr')
    qs = Toilette.objects.all()
    if pmr == '1': qs = qs.filter(acces_pmr=True)
    if bebe == '1': qs = qs.filter(relais_bebe=True)
    if arr: qs = qs.filter(arrondissement=f"750{arr.zfill(2)}")
    data = [
        {
            'type': t.type,
            'adresse': t.adresse,
            'pmr': t.acces_pmr,
            'bebe': t.relais_bebe,
            'lat': t.latitude,
            'lng': t.longitude
        } for t in qs
    ]
    return JsonResponse(data, safe=False)