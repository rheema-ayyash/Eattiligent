import csv
from django.core.management.base import BaseCommand
from recipes.models import DietaryRestriction, Ingredient, Dietary_Restriction_Ingredient


class Command(BaseCommand):
    help="Import dietary restriction ingredients from data/raw/dietary_restriction_ingredients.csv"

    def handle(self, *args, **kwargs):
        file_path="data/raw/dietary_restriction_ingredients.csv"

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader=csv.DictReader(csvfile)

            for row in reader:
                restriction_id=row["Dietary_Restriction_ID"].strip()
                ingredient_id=row["Ingredient_ID"].strip()

                if not restriction_id or not ingredient_id:
                    continue

                try:
                    dietary_restriction=DietaryRestriction.objects.get(id=int(restriction_id))
                    ingredient=Ingredient.objects.get(id=int(ingredient_id))
                except DietaryRestriction.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"DietaryRestriction {restriction_id} not found. Skipping."))
                    continue
                except Ingredient.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Ingredient {ingredient_id} not found. Skipping."))
                    continue

                Dietary_Restriction_Ingredient.objects.update_or_create(
                    dietary_restriction=dietary_restriction,
                    ingredient=ingredient,
                )

        self.stdout.write(self.style.SUCCESS("Dietary restriction ingredients imported successfully."))