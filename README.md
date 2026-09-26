# CSC394 Final Project Nutrition App

command to import recepies
docker-compose exec web python manage.py import_recipes "data/raw/recipes.csv"

to import dieseases
docker-compose exec web python manage.py import_diseases "data/raw/diseases.csv"

import ingredients 
docker-compose exec web python manage.py import_ingredients "data/raw/ingredients.csv"

import avoid foods
docker-compose exec web python manage.py import_disease_avoid_food "data/raw/disease_avoid_food.csv"

import super foods
docker-compose exec web python manage.py import_disease_super_food "data/raw/disease_super_food.csv"

import recipe ingredients table
docker-compose exec web python manage.py import_recipe_ingredients "data/raw/recipe_ingredients.csv"


docker-compose exec web python manage.py import_recipes "data/raw/recipes.csv"
docker-compose exec web python manage.py import_diseases "data/raw/diseases.csv"
docker-compose exec web python manage.py import_ingredients "data/raw/ingredients.csv"
docker-compose exec web python manage.py import_recipe_ingredients "data/raw/recipe_ingredients.csv"
docker-compose exec web python manage.py import_disease_avoid_food "data/raw/disease_avoid_food.csv"
docker-compose exec web python manage.py import_disease_super_food "data/raw/disease_super_food.csv"

from django.contrib.auth.models import User
from recipes.models import DailyLog, MealEntry, WorkoutEntry
from datetime import date, timedelta
import random

user = User.objects.first()  # change this to target a specific user

for i in range(7):
    log_date = date.today() - timedelta(days=i)
    calories = round(random.uniform(1500, 2500), 1)
    protein = round(random.uniform(50, 150), 1)
    carbs = round(random.uniform(150, 350), 1)
    fats = round(random.uniform(40, 100), 1)
    burned = round(random.uniform(0, 500), 1)
    log, created = DailyLog.objects.get_or_create(
        user=user,
        date=log_date,
        defaults={
            'total_calories': calories,
            'total_protein': protein,
            'total_carbs': carbs,
            'total_fats': fats,
            'total_burned': burned,
            'calorie_goal': 2000,
        }
    )
    if created:
        MealEntry.objects.create(
            daily_log=log,
            meal_name=f'Sample Meal',
            calories=calories,
            protein=protein,
            carbs=carbs,
            fats=fats,
        )
        WorkoutEntry.objects.create(
            daily_log=log,
            workout_type=random.choice(['cardio', 'strength', 'walking', 'running']),
            calories_burned=burned,
        )
        print(f'Created log for {log_date}')
    else:
        print(f'Log already exists for {log_date}, skipping.')


from django.contrib.auth.models import User
from recipes.models import DailyLog, MealEntry, WorkoutEntry
from datetime import date, timedelta
import random
user = User.objects.first()  # change to target a specific user
workout_counts = random.sample(range(1, 11), 7)
for i in range(7):
    log_date = date.today() - timedelta(days=i)
    calories = round(random.uniform(1500, 2500), 1)
    protein = round(random.uniform(50, 150), 1)
    carbs = round(random.uniform(150, 350), 1)
    fats = round(random.uniform(40, 100), 1)
    burned = round(random.uniform(0, 500), 1)
    log, created = DailyLog.objects.update_or_create(
        user=user,
        date=log_date,
        defaults={
            'total_calories': calories,
            'total_protein': protein,
            'total_carbs': carbs,
            'total_fats': fats,
            'total_burned': burned,
            'calorie_goal': 2000,
        }
    )
    MealEntry.objects.filter(daily_log=log).delete()
    WorkoutEntry.objects.filter(daily_log=log).delete()
    MealEntry.objects.create(
        daily_log=log,
        meal_name=f'Sample Meal',
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats,
    )
    num_workouts = workout_counts[i]
    for _ in range(num_workouts):
        WorkoutEntry.objects.create(
            daily_log=log,
            workout_type=random.choice(['cardio', 'strength', 'walking', 'running']),
            calories_burned=round(random.uniform(100, 500), 1),
        )
    print(f'{"Created" if created else "Updated"} log for {log_date} with {num_workouts} workouts')