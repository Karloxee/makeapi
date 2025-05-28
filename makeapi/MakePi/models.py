from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    email = models.EmailField(unique=True)  # Assure l'unicité des adresses email
    actif = models.BooleanField(default=True)  # Indique si l'utilisateur est actif

    # Redéfinir les relations ManyToMany pour éviter les conflits de reverse accessor
    groups = models.ManyToManyField(
        Group,
        related_name="makepi_user_set",  # Ce related_name personnalisé évite les collisions avec auth.User.groups
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="makepi_user_set",  # Personnalisation du related_name pour éviter les conflits
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.username

class Toilette(models.Model):
    """Modèle pour représenter les toilettes publiques"""
    type = models.CharField(max_length=100, blank=True)
    adresse = models.TextField(blank=True)
    arrondissement = models.CharField(max_length=2, blank=True)  # Ex : '01', '12'
    horaires = models.CharField(max_length=255, blank=True)
    acces_pmr = models.BooleanField(default=False)
    relais_bebe = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} - {self.adresse}"
