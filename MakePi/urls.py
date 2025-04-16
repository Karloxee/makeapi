"""
URL configuration for MakePi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MakePi import  views   


urlpatterns = [path('', views.toindex, name='index')
              , path('index/', views.index, name='index')
              , path('generic/', views.generic, name='generic')
              , path('question1/', views.question1, name='nbr_arr')
               , path('question2/', views.question2, name='type_arr')
                , path('question3/', views.question3, name='pmr_arr')
                , path('map/', views.map, name='map')
             , path('inscription/', views.inscription, name='inscription')
              , path('contact/', views.contact, name='contact')
              , path('sinscrire/', views.sinscrire, name='inscription')
                , path('admin/' ,views.admin, name='administration')
                 , path('seconnecter/', views.seconnecter, name='inscription')
                 , path('logout/', views.logout, name='deconnexion')
                 , path('logout_admin/', views.logout_admin, name='deconnexionAdmin')
                 , path('display/', views.display, name='affichage')
                 ,path('delete/<int:id_user>/', views.delete_user, name='suppression')
       ,path('disable/<int:id_user>/', views.desactiver_user, name='desactivation')
         ,path('enable/<int:id_user>/', views.activer_user, name='activation')
         ,path('envoyer_msg/', views.envoyer_msg, name='envoi_de_message')
         ,path('messages/', views.messages, name='select_all_message')
          ,path('lire_message/<int:id_msg>/', views.lire_message, name='lire_message')
         
]
