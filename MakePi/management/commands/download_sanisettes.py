# myapp/management/commands/download_sanisettes.py
import os
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Télécharge le CSV sanisettes_paris depuis l'OpenData Paris et l'enregistre dans static/csv/"

    def handle(self, *args, **options):
        # URL de l'export CSV Opendata Paris
        url = (
            "https://opendata.paris.fr/api/explore/v2.1/"
            "catalog/datasets/sanisettesparis/exports/csv"
            "?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
        )
        # Chemin de sortie local
        output_dir = os.path.join(settings.BASE_DIR, 'static', 'csv')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'sanisettes_paris.csv')

        self.stdout.write(f"Téléchargement du CSV depuis {url}...")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            raise CommandError(f"Erreur lors du téléchargement : {e}")

        with open(output_path, 'wb') as f:
            f.write(response.content)

        self.stdout.write(self.style.SUCCESS(
            f"CSV téléchargé et enregistré sous {output_path}"
        ))
