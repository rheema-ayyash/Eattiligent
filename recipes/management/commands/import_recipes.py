from django.core.management.base import BaseCommand
import csv
from recipes.models import Recipe


def to_float(val):
    """Convert string to float, return None if empty or invalid."""
    try:
        return float(val) if val not in (None, '', ' ') else None
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Import recipes from CSV"

    def add_arguments(self, parser):
        parser.add_argument('csvpath')

    def handle(self, *args, **opts):
        path = opts['csvpath']
        count = 0
        with open(path, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                recipe_id = int(row.get("ID", 0) or 0)
                if not recipe_id:
                    continue
                
                # The CSV has an empty column after Title that contains meal_type
                meal_type = row.get("Meal_Time", "") or ""

                defaults = {
                    "title": row.get("Title", "").strip(),
                    "meal_type": meal_type.strip(),
                    "ingredients": row.get("Ingredients", "").strip(),
                    "how_to_cook": row.get("How_To_Cook", "").strip(),
                 }
                
                Recipe.objects.update_or_create(id=recipe_id, defaults=defaults)
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} recipes'))
