from django.core.management.base import BaseCommand
import csv
from recipes.models import Disease


def to_float(val):
    try:
        return float(val) if val not in (None, '', ' ') else None
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Import diseases from CSV"

    def add_arguments(self, parser):
        parser.add_argument('csvpath')

    def handle(self, *args, **opts):
        path = opts['csvpath']
        count = 0

        with open(path, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                disease_id = int(row.get('ID', 0) or 0)
                if not disease_id:
                    continue
                defaults = {
                    'title': row.get('Title', ''),
                    'description': row.get('Description', ''),
                    'related_diseases': row.get('related_diseases', ''),

                    # Low stats
                    'low_calories_kcal': to_float(row.get('low_calories_kcal')),
                    'low_saturated_fat_g': to_float(row.get('low_saturated_fat_g')),
                    'low_carbs_g': to_float(row.get('low_carbs_g')),
                    'low_protein_g': to_float(row.get('low_protein_g')),
                    'low_fiber_g': to_float(row.get('low_fiber_g')),
                    'low_sugar_g': to_float(row.get('low_sugar_g')),
                    'low_cholesterol_mg': to_float(row.get('low_cholesterol_mg')),
                    'low_sodium_mg': to_float(row.get('low_sodium_mg')),
                    'low_potassium_mg': to_float(row.get('low_potassium_mg')),
                    'low_iron_mg': to_float(row.get('low_iron_mg')),
                    'low_calcium_mg': to_float(row.get('low_calcium_mg')),
                    'low_phosphorus_mg': to_float(row.get('low_phosphorus_mg')),
                    'low_magnesium_mg': to_float(row.get('low_magnesium_mg')),
                    'low_vitamin_a_ug': to_float(row.get('low_vitamin_a_ug')),
                    'low_vitamin_b_mg': to_float(row.get('low_vitamin_b_mg')),
                    'low_vitamin_c_mg': to_float(row.get('low_vitamin_c_mg')),
                    'low_vitamin_d_ug': to_float(row.get('low_vitamin_d_ug')),
                    'low_vitamin_e_mg': to_float(row.get('low_vitamin_e_mg')),
                    'low_vitamin_k_ug': to_float(row.get('low_vitamin_k_ug')),
                    'low_zinc_mg': to_float(row.get('low_zinc_mg')),
                    'low_iodine_ug': to_float(row.get('low_iodine_ug')),
                    'low_selenium_ug': to_float(row.get('low_selenium_ug')),
                    'low_copper_mg': to_float(row.get('low_copper_mg')),
                    'low_fluoride_mg': to_float(row.get('low_fluoride_mg')),
                    'low_chromium_mg': to_float(row.get('low_chromium_mg')),

                    # High stats
                    'high_calories_kcal': to_float(row.get('high_calories_kcal')),
                    'high_saturated_fat_g': to_float(row.get('high_saturated_fat_g')),
                    'high_carbs_g': to_float(row.get('high_carbs_g')),
                    'high_protein_g': to_float(row.get('high_protein_g')),
                    'high_fiber_g': to_float(row.get('high_fiber_g')),
                    'high_sugar_g': to_float(row.get('high_sugar_g')),
                    'high_cholesterol_mg': to_float(row.get('high_cholesterol_mg')),
                    'high_sodium_mg': to_float(row.get('high_sodium_mg')),
                    'high_potassium_mg': to_float(row.get('high_potassium_mg')),
                    'high_iron_mg': to_float(row.get('high_iron_mg')),
                    'high_calcium_mg': to_float(row.get('high_calcium_mg')),
                    'high_phosphorus_mg': to_float(row.get('high_phosphorus_mg')),
                    'high_magnesium_mg': to_float(row.get('high_magnesium_mg')),
                    'high_vitamin_a_ug': to_float(row.get('high_vitamin_a_ug')),
                    'high_vitamin_b_mg': to_float(row.get('high_vitamin_b_mg')),
                    'high_vitamin_c_mg': to_float(row.get('high_vitamin_c_mg')),
                    'high_vitamin_d_ug': to_float(row.get('high_vitamin_d_ug')),
                    'high_vitamin_e_mg': to_float(row.get('high_vitamin_e_mg')),
                    'high_vitamin_k_ug': to_float(row.get('high_vitamin_k_ug')),
                    'high_zinc_mg': to_float(row.get('high_zinc_mg')),
                    'high_iodine_ug': to_float(row.get('high_iodine_ug')),
                    'high_selenium_ug': to_float(row.get('high_selenium_ug')),
                    'high_copper_mg': to_float(row.get('high_copper_mg')),
                    'high_fluoride_mg': to_float(row.get('high_fluoride_mg')),
                    'high_chromium_mg': to_float(row.get('high_chromium_mg')),
                }

                Disease.objects.update_or_create(id=disease_id, defaults=defaults)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} diseases"))
        