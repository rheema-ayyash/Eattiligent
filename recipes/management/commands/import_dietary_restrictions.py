import csv
from django.core.management.base import BaseCommand
from recipes.models import DietaryRestriction


class Command(BaseCommand):
    help="Import dietary restrictions from data/raw/dietary_restrictions.csv"

    def handle(self, *args, **kwargs):
        file_path="data/raw/dietary_restrictions.csv"

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader=csv.DictReader(csvfile)

            for row in reader:
                restriction_id=row["Id"].strip()
                title=row["Title"].strip()

                if not restriction_id or not title:
                    continue

                DietaryRestriction.objects.update_or_create(
                    id=int(restriction_id),
                    defaults={
                        "title": title,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Dietary restrictions imported successfully."))