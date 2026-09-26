from django.core.management.base import BaseCommand
import csv
from recipes.models import Ingredient


def to_float(val):
    try:
        return float(val) if val not in (None, "", " ") else None
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Import ingredients from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csvpath")

    def handle(self, *args, **opts):
        path = opts["csvpath"]
        count = 0

        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)

            for row in reader:
                
                ingredient_id = int(row.get("Id", 0) or 0)
                if not ingredient_id:
                    continue

                amount = (row.get("Amount") or "").strip()
                unit = (row.get("Type_of_Measurement") or "").strip()
                #measurement_value = f"{amount} {unit}".strip() if (amount or unit) else None

                defaults = {
                   
                    "title": (row.get("Name") or "").strip(),

                    "measurements": unit,

                    "measurement_amount": amount,

                    
                    "calories_kcal": to_float(row.get("Calories_kcal")),
                    "saturated_fat_g": to_float(row.get("Saturated_Fat_g")),
                    "carbs_g": to_float(row.get("Carbs_g")),
                    "protein_g": to_float(row.get("Protein_g")),
                    "fiber_g": to_float(row.get("Fiber_g")),
                    "sugar_g": to_float(row.get("Sugar_g")),

                   
                    "cholesterol_mg": to_float(row.get("cholesterol_mg")),
                    "sodium_mg": to_float(row.get("sodium_mg")),
                    "potassium_mg": to_float(row.get("potassium_mg")),

                    "iron_mg": to_float(row.get("Iron_mg")),
                    "calcium_mg": to_float(row.get("Calcium_mg")),
                    "phosphorus_mg": to_float(row.get("Phosphorus_mg")),

                    
                    "magnesium_mg": to_float(row.get("magnesium_mg")),

                    "vitamin_a_ug": to_float(row.get("Vitamin_A_ug")),

                    
                    "vitamin_b_mg": to_float(row.get("vitamin_b_mg")),

                    "vitamin_c_mg": to_float(row.get("Vitamin_C_mg")),
                    "vitamin_d_ug": to_float(row.get("Vitamin_D_ug")),
                    "vitamin_e_mg": to_float(row.get("Vitamin_E_mg")),
                    "vitamin_k_ug": to_float(row.get("Vitamin_K_ug")),

                    "zinc_mg": to_float(row.get("Zinc_mg")),
                    "iodine_ug": to_float(row.get("Iodine_ug")),
                    "selenium_ug": to_float(row.get("Selenium_ug")),
                    "copper_mg": to_float(row.get("Copper_mg")),
                    "fluoride_mg": to_float(row.get("Fluoride_mg")),
                    "chromium_mg": to_float(row.get("Chromium_mg")),
                }

                Ingredient.objects.update_or_create(id=ingredient_id, defaults=defaults)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} ingredients"))