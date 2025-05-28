from django.contrib import admin
from django.urls import path, include  # ⬅️ important : il faut include
from MakePi import views

urlpatterns = [
    # Intégration de django-prometheus : doit être AVANT tout
    path('', include('django_prometheus.urls')),  # <-- essentiel pour /metrics

    # Tes routes existantes
    path('', views.toindex, name='index'),
    path('index/', views.index, name='index'),
    path('generic/', views.generic, name='generic'),
    path('question1/', views.question1, name='nbr_arr'),
    path('question2/', views.question2, name='type_arr'),
    path('question3/', views.question3, name='pmr_arr'),
    path('map/', views.map, name='map'),
    path('inscription/', views.inscription, name='inscription'),
    path('contact/', views.contact, name='contact'),
    path('sinscrire/', views.sinscrire, name='inscription'),
    path('admin/', views.admin, name='administration'),
    path('seconnecter/', views.seconnecter, name='inscription'),
    path('logout/', views.logout, name='deconnexion'),
    path('logout_admin/', views.logout_admin, name='deconnexionAdmin'),
    path('display/', views.display, name='affichage'),
    path('delete/<int:id_user>/', views.delete_user, name='suppression'),
    path('disable/<int:id_user>/', views.desactiver_user, name='desactivation'),
    path('enable/<int:id_user>/', views.activer_user, name='activation'),
    path('envoyer_msg/', views.envoyer_msg, name='envoi_de_message'),
    path('messages/', views.messages, name='select_all_message'),
    path('lire_message/<int:id_msg>/', views.lire_message, name='lire_message'),
]