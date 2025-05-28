def main():
    pass
if __name__=='__main__':
    main()

#il faut charger la librairie pandas
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
import plotly as px


dossier_execution = os.path.dirname(os.path.abspath(__file__)) 

if sd.creation_date_today() == False:
    sd.save_data_from_online()

df = pd.read_csv(dossier_execution + "/sanisettes_paris.csv",sep=';',header=0)
df = df.drop('URL_FICHE_EQUIPEMENT', axis=1)
df = df.drop('geo_shape', axis=1)
df = df.drop('geo_point_2d', axis=1)
df = df.drop('STATUT', axis=1)

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

df['ACCES_PMR'] = df['ACCES_PMR'].apply(modifier_valeur)
df['RELAIS_BEBE'] = df['RELAIS_BEBE'].apply(modifier_valeur)
df['ARRONDISSEMENT'] = df['ARRONDISSEMENT'].apply(split_arr)
df['HORAIRE'] = df['HORAIRE'].apply(modifier_horaire)

#copie de la colonne arrondissement en DataFrame
df_toilette_arrondissement = pd.DataFrame(df['ARRONDISSEMENT'].sort_values()) # trie les arrondissements
df_toilette_arrondissement['ARRONDISSEMENT']=df_toilette_arrondissement['ARRONDISSEMENT'].apply(arr_tostring)

# compter le nombre de toilettes par arrondissement
nombre_toilette_arrondissement = df_toilette_arrondissement[df_toilette_arrondissement['ARRONDISSEMENT'] == "18"].shape[0] # attention valeur du  ==
sns.set_theme(style="darkgrid")
gt_nb_toilette_by_arrondissement = sns.histplot(data=df_toilette_arrondissement, x="ARRONDISSEMENT", discrete=True,  shrink=.5 ) #shrink = largeur de la colonne

# affichage de la valeur max en haut de chaque colonne
gt_nb_toilette_by_arrondissement.bar_label(gt_nb_toilette_by_arrondissement.containers[0], fontsize=10)

#rotation affichage des x
plt.xticks(rotation=30)
plt.title("Nombre de toilettes par arrondissement")
plt.xlabel("Arrondissements")
plt.ylabel("Toilettes")

# Calculer le nombre de toilettes par arrondissement
toilettes_par_arrondissement = df_toilette_arrondissement["ARRONDISSEMENT"].value_counts().reset_index()
toilettes_par_arrondissement.columns = ['Arrondissement', 'Nombre de toilettes']

# Créer le graphique camembert interactif avec Plotly Express
fig = px.pie(toilettes_par_arrondissement, values='Nombre de toilettes', names='Arrondissement', title='Répartition du nombre de toilettes par arrondissement à Paris')
fig.show()


# type de toilettes par arrondissement
sns.set_theme(style="darkgrid")
plt.subplots(figsize=(12,8))
df_type_arrondissement= df.groupby(['TYPE', 'ARRONDISSEMENT']).size().reset_index(name='COUNT') #group by type and arrondissement
gt_type_by_arrondissement=sns.barplot(data=df_type_arrondissement, x='ARRONDISSEMENT', y='COUNT', hue='TYPE',width=1) #hue:legend, si N width trop grand,trop de temps 
#pour present tous les valeurs de bar chart
for containers in gt_type_by_arrondissement.containers:
    gt_type_by_arrondissement.bar_label(containers, fontsize=9) 
plt.title("Types des Toilettes par arrondissement")
plt.xlabel("Arrondissement")
plt.xticks(rotation=30)
plt.ylabel("Nombre de Toilettes")  
plt.show()


# Acces_pmr & relais_bebe
labels = ['Acces','Pas d\'acces']
df_PMR=df['ACCES_PMR'].value_counts()
df_BEBE=df['RELAIS_BEBE'].value_counts()
colors = sns.color_palette('pastel')
fig, pie=plt.subplots(1, 2, figsize=(14, 6))

pie[0].pie(df_PMR, labels=labels, colors = colors, autopct=lambda pct: f"{pct:.1f}% ({int(pct/100*sum(df_PMR))})")
pie[0].set_title("Toilettes avec acces PMR")
pie[0].legend( loc = 'lower right', labels=labels)

pie[1].pie(df_BEBE, labels=labels, colors = colors, autopct=lambda pct: f"{pct:.1f}% ({int(pct/100*sum(df_BEBE))})")
pie[1].set_title("Toilettes avec relais Bébé")
pie[1].legend( loc = 'lower right', labels=labels)

plt.show()

#####Pourcentage de toilettes ayant accès PMR###
pourcentage_AccesPMR = (df['ACCES_PMR'] == 1).mean() * 100
nbr_acc=(df['ACCES_PMR'] == 1).value_counts()
comptages = nbr_acc.values.tolist()
labels = [f'Accès PMR: {comptages[0]}', f'Pas d\'accès PMR: {comptages[1]}']
sizes = [pourcentage_AccesPMR, 100 - pourcentage_AccesPMR]

plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title('Pourcentage de toilettes ayant accès PMR')
plt.show()
