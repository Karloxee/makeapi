from django.core.management.base import BaseCommand
from MakePi.models import Toilette
import csv
import os

class Command(BaseCommand):
    help = "Importe les données des toilettes depuis le fichier CSV local"

    def handle(self, *args, **kwargs):
        file_path = 'static/csv/sanisettes_paris.csv'

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Fichier CSV non trouvé : {file_path}"))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            count = 0

            for row in reader:
                coords = row.get("geo_point_2d", "")
                if coords and "," in coords:
                    lat, lon = map(float, coords.split(","))
                else:
                    lat, lon = None, None

                toilette = Toilette(
                    type=row.get("type", "") or "",
                    adresse=row.get("adresse", "") or "",
                    arrondissement=(row.get("ARRONDISSEMENT", "") or "").zfill(2),
                    horaires=row.get("horaires", "") or "",
                    acces_pmr=(row.get("ACCES_PMR", "").strip().lower() == "oui"),
                    relais_bebe=(row.get("RELAIS_BEBE", "").strip().lower() == "oui"),
                    latitude=lat,
                    longitude=lon
                )
                toilette.save()
                count += 1

            self.stdout.write(self.style.SUCCESS(f"{count} toilettes importées avec succès."))



