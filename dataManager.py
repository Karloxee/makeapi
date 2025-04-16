# !/python3.12
# -*- coding: utf-8 -*-
#
import psycopg2


class PostgreSQL():
    def __init__(self, dataBase):
        self.dataBase = dataBase

    def setConnexion(self):
        try:
            self.connexion = psycopg2.connect( user = "matthieu"
                                             , password = "postgres"
                                             , host = "localhost"
                                             , port = "5432"
                                             , database = self.dataBase
                                             )
            self.cursor = self.connexion.cursor()
        except psycopg2.Error as err:
            print("! PostgreSQL setConnexion() error : ", err)

    def selectAll(self,table):
        try:
            sql = "select * from " + table + " order by id;"
            print(sql)
            self.cursor.execute(sql)
            ''' restitue la liste résultante de la selection de données '''
            dataSet = self.cursor.fetchall()
            print("dataSet:", dataSet)
            return dataSet
        except psycopg2.Error as err:
            print("! PostgreSQL selectAll() error : ", err)

    def  select_user(self,requette):
        try:
           
            sql = requette
           
            self.cursor.execute(sql)
           
            resultat =  self.cursor.fetchone()
            
            return resultat[0] if resultat else 0
        except psycopg2.Error as err:
            return None

    def  select_nameOfuser(self,requette):
        try:
            sql = requette
            
            self.cursor.execute(sql)
            
            resultat =  self.cursor.fetchone()
            return resultat[0] if resultat else None
        except psycopg2.Error as err:
            return None

    def  select_IdOfuser(self,requette):
        try:
            sql = requette
            
            self.cursor.execute(sql)
            
            resultat =  self.cursor.fetchone()
            return resultat[0] if resultat else None
        except psycopg2.Error as err:
            return None

    def selectAllmsg(self):
        try:
            sql = "select u.nom,m.objet,m.statut,m.id from messages m inner join users u on m.id_user=u.id order by m.date_message desc; "
            self.cursor.execute(sql)
            ''' restitue la liste résultante de la selection de données '''
            dataSet = self.cursor.fetchall()
            print("dataSet:", dataSet)
            return dataSet
        except psycopg2.Error as err:
            print("! PostgreSQL selectAll() error : ", err)

    def selectmsg(self,id_msg):
        try:
            req=f"update messages set statut='y' where id={id_msg}"
            self.Execute_requette(req)
            sql = f"select u.nom,m.objet,m.messages,TO_CHAR(m.date_message, 'DD-MM-YYY HH24:MI:SS') from messages m inner join users u on m.id_user=u.id where m.id={id_msg}; "

            self.cursor.execute(sql)
            ''' restitue la liste résultante de la selection de données '''
            dataSet = self.cursor.fetchall()
            print("dataSet:", dataSet)
            return dataSet
        except psycopg2.Error as err:
            print("! PostgreSQL selectAll() error : ", err)

    def closeConnexion(self):
        try:
            self.cursor.close()
            self.connexion.close()
        except psycopg2.Error as err:
            print("! PostgreSQL closeConnexion() error : ", err)

    def Execute_requette(self,requette) :
        try:
            self.cursor.execute(requette)
            self.connexion.commit()
            return True
        except psycopg2.Error as err:
            return False

    def insertInto(self,sqlInsertInto):
        try:
            self.cursor.execute(sqlInsertInto)
            self.connexion.commit()
            return True
        except psycopg2.Error as err:
            return False