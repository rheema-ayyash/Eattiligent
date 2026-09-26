from django.core.management.base import BaseCommand
import csv
from recipes.models import Disease_Avoid_Food


class Command(BaseCommand):
    help = "Import disease avoid food mapping from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csvpath")

    def handle(self, *args, **opts):
        path = opts["csvpath"]
        count = 0

        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)

            for row in reader:
                disease_id = int(row.get("disease_id", 0) or 0)
                ingredient_id = int(row.get("ingredient_id", 0) or 0)

                if not disease_id or not ingredient_id:
                    continue

                Disease_Avoid_Food.objects.update_or_create(
                    disease_id_id=disease_id,
                    ingredient_id_id=ingredient_id,

                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported {count} disease avoid food rows")
        )