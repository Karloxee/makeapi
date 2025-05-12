# MakePi/urls.py
from django.contrib import admin
from django.urls import path
from MakePi import views

app_name = 'MakePi'

urlpatterns = [

    # API pour filtrage des toilettes
    path('api/toilettes/', views.toilettes_api, name='toilettes_api'),

    # Page d'accueil
    path('',               views.index,               name='index'),
    path('index/',         views.index,               name='index'),

    # Page "Qui sommes-nous?"
    path('generic/',       views.generic,             name='generic'),

    # Carte interactive
    path('map/',           views.map,                 name='map'),

    # Graphiques dynamiques
    path('question1/',      views.question1_view,      name='nbr_arr'),
    path('question1/data/', views.question1_data,      name='nbr_arr_data'),

    path('question2/',      views.question2_view,      name='type_arr'),
    path('question2/data/', views.question2_data,      name='type_arr_data'),

    path('question3/',      views.question3_view,      name='pmr_arr'),
    path('question3/data/', views.question3_data,      name='pmr_arr_data'),

    # Inscription & authentification
    path('inscription/',   views.inscription,         name='inscription'),
    path('sinscrire/',     views.sinscrire,           name='sinscrire'),
    path('seconnecter/',   views.seconnecter,         name='seconnecter'),
    path('contact/',       views.contact,             name='contact'),
    path('logout/',        views.logout,              name='logout'),
    path('logout_admin/',  views.logout_admin,        name='logout_admin'),

    # Administration utilisateur
    path('admin/', views.admin,              name='administration'),

    # Messages
    path('envoyer_msg/',   views.envoyer_msg,         name='envoyer_msg'),
    path('messages/',      views.messages,            name='messages'),
    path('lire_message/<int:id_msg>/', views.lire_message, name='lire_message'),

    # Gestion utilisateurs
    path('display/',       views.display,             name='display'),
    path('delete/<int:id_user>/',   views.delete_user,    name='delete_user'),
    path('disable/<int:id_user>/',  views.desactiver_user,name='desactiver_user'),
    path('enable/<int:id_user>/',   views.activer_user,   name='activer_user'),
]
