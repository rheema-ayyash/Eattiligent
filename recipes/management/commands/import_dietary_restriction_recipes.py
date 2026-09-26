import csv
from django.core.management.base import BaseCommand
from recipes.models import DietaryRestriction, Recipe, Dietary_Restriction_Recipe


class Command(BaseCommand):
    help="Import dietary restriction recipes from data/raw/dietary_restriction_recipes.csv"

    def handle(self, *args, **kwargs):
        file_path="data/raw/dietary_restriction_recipes.csv"

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader=csv.DictReader(csvfile)

            for row in reader:
                restriction_id=row["Dietary_restriction_id"].strip()
                recipe_id=row["recipe_id"].strip()

                if not restriction_id or not recipe_id:
                    continue

                try:
                    dietary_restriction=DietaryRestriction.objects.get(id=int(restriction_id))
                    recipe=Recipe.objects.get(id=int(recipe_id))
                except DietaryRestriction.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"DietaryRestriction {restriction_id} not found. Skipping."))
                    continue
                except Recipe.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Recipe {recipe_id} not found. Skipping."))
                    continue

                Dietary_Restriction_Recipe.objects.update_or_create(
                    dietary_restriction=dietary_restriction,
                    recipe=recipe,
                )

        self.stdout.write(self.style.SUCCESS("Dietary restriction recipes imported successfully."))