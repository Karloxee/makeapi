# MakePi/models.py

from django.db import models

class Toilette(models.Model):
    type = models.CharField(max_length=100, blank=True)
    adresse = models.TextField(blank=True)
    arrondissement = models.CharField(max_length=5, blank=True) 
    horaires = models.CharField(max_length=255, blank=True)
    acces_pmr = models.BooleanField(default=False)
    relais_bebe = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} - {self.adresse}"
    
    class Meta:
        db_table = "toilettes"