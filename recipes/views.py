import json
import random
import re
from django.db.models.manager import BaseManager
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote

from urllib3 import request
import recipes
from recipes.models import Disease, Goal, AppUser, Disease_Avoid_Food, Ingredient, Recipe_Ingredients, UserPickedRecipes, UserPickedDisease, Disease_Super_Food,DailyLog, WorkoutEntry
from recipes.models import Recipe
from nutrition_project.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta
from recipes.models import DailyLog, MealEntry, WorkoutEntry, WeightEntry
from django.utils import timezone
from recipes.models import Disease, AppUser, Disease_Avoid_Food, Ingredient, Recipe_Ingredients, UserPickedRecipes, Disease_Super_Food
from recipes.models import Quote
import random

def home(request):
    quote = None
    if request.user.is_authenticated:
        # Get random quote from database
        quotes = Quote.objects.all()
        if quotes.exists():
            quote = random.choice(list(quotes))
        else:
            # Default quote if none in database
            quote = type('obj', (object,), {
                'quote': 'Your health is your wealth. Invest in it daily.',
            })
    
    return render(request, 'main/home.html', {'quote': quote})
def landing_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    return render(request, 'main/landingpage.html',
                  {'app_name': 'Eattiligent',
                   'user_email': 'Login'})


# login
def login_page(request):
    error_info = {"errors": {}, "email": ""}

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        error_info["email"] = email

        try:
            validate_email(email)
        except ValidationError:
            error_info["errors"]["email"] = "Not a valid email address"

        if not password:
            error_info["errors"]["password"] = "Not a valid password"

        if not error_info["errors"]:
            user_info = authenticate(request, username=email, password=password)

            if user_info is None:
                error_info["errors"]["login"] = "Invalid email or password"
            else:
                auth_login(request, user_info)

                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                return redirect("home")

    return render(request, "main/login.html", error_info)


# logout
def logout_view(request):
    logout(request)
    return redirect("login_page")

# registration
def registration_page(request):
    form_data = {
        "email": "", "weight": "", "goal_weight": "", "bmr" : "", "dietary_restriction": "", 
        "allergy": "", "meals_per": "", "snacks_per": ""
    }
    error_info = {"errors": {}}
    #error_info = {"errors": {}, "email": ""}
    diseases = Disease.objects.all()

    if request.method == "POST":
        for fields in form_data.keys():
            form_data[fields] = request.POST.get(fields, "").strip()

        email = form_data["email"].lower()
        password = request.POST.get("password", "")
        confirm_pass = request.POST.get("confirm_pass", "")
        disease_id = request.POST.get("disease")

        if not email:
            error_info["errors"]["email"] = "Email is required"
        else:
            try:
                validate_email(email)
                if User.objects.filter(username=email).exists():
                    error_info["errors"]["email"] = "Email already exists"
            except ValidationError:
                error_info["errors"]["email"] = "Not a valid email address"

        if not password:
            error_info["errors"]["password"] = "Password is required"
        if password != confirm_pass:
            error_info["errors"]["confirm_pass"] = "Passwords do not match"
            
        if not error_info["errors"]:
            try:
                user = User.objects.create_user(username=email, email=email, password=password)
                app_user = AppUser.objects.create(
                    user=user,
                    bmr=float(form_data["bmr"]) if form_data["bmr"] else None,
                    dietary_restriction=form_data["dietary_restriction"] or None,
                    weight=float(form_data["weight"]) if form_data["weight"] else None,
                    goal_weight=float(form_data["goal_weight"]) if form_data["goal_weight"] else None,
                    allergy=form_data["allergy"] or None,
                    meals_per=int(form_data["meals_per"]) if form_data["meals_per"] else None,
                    snacks_per=int(form_data["snacks_per"]) if form_data["snacks_per"] else None
                
                ) #user_disease = None
                if disease_id and disease_id.isdigit():
                    try:
                        user_disease = Disease.objects.get(id=disease_id)
                        UserPickedDisease.objects.create(user=app_user, disease=f"{user_disease.title}]")
                        app_user.diseases.set([user_disease])
                    except Disease.DoesNotExist:
                        error_info["errors"]["disease"] = "Selected disease is not valid"

                return redirect("login_page")
            except Exception as e:
                print(f"Registration Error: {e}")
                error_info["errors"]["registration"] = f"Database error: {e}"

    
    all = {**error_info, "diseases": diseases}
    return render(request, 'main/register.html', all)


def search_page(request):
    return render(request, 'recipes/searchpage.html')


def recipes_list(request):
    recipes = list(Recipe.objects.all().order_by('title'))
    desired_serving = request.GET.get('servings')

    if request.user.is_authenticated:
        try:
            app_user = AppUser.objects.get(user=request.user)

            try:
                user_picks = UserPickedDisease.objects.get(user=app_user)
                picked_disease = [d for d in user_picks.disease.rstrip("]").split("]") if d]
                user_disease_ids = Disease.objects.filter(title__in=picked_disease).values_list('id', flat=True)
            except UserPickedDisease.DoesNotExist:
                user_disease_ids = []

            avoid_ingredient_ids = Disease_Avoid_Food.objects.filter(
                disease_id__in=user_disease_ids
            ).values_list('ingredient_id', flat=True)

            if avoid_ingredient_ids:
                avoided_recipe_ids = Recipe_Ingredients.objects.filter(
                    ingredient_id__in=avoid_ingredient_ids
                ).values_list('recipe_id', flat=True)
                recipes = list(Recipe.objects.all().order_by('title').exclude(id__in=avoided_recipe_ids))

        except AppUser.DoesNotExist:
            pass

    # Build nutrition list — always runs, same size/order as recipes
    nutrition_list = []
    for recipe in recipes:
        try:
            #amount = desired_serving if desired_serving else recipe.serving
            amount = float(desired_serving) if desired_serving else 1.0
        except (ValueError, TypeError):
            amount = 1.0
        #scale = recipe.scale_ingredients(amount)

        recipe_ingredients = Recipe_Ingredients.objects.filter(recipe_id=recipe).select_related('ingredient_id')
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fiber = 0
        total_saturated_fat_g = 0
        
        for ri in recipe_ingredients:
            factor = float(ri.amount or 0) * amount
            total_calories += (ri.ingredient_id.calories_kcal or 0) * factor
            total_protein += (ri.ingredient_id.protein_g or 0) * factor
            total_carbs += (ri.ingredient_id.carbs_g or 0) * factor
            total_fiber += (ri.ingredient_id.fiber_g or 0) * factor
            total_saturated_fat_g += (ri.ingredient_id.saturated_fat_g or 0) * factor
        # total_calories = sum((ri.ingredient_id.calories_kcal or 0) * scale for ri in recipe_ingredients)
        # total_protein = sum((ri.ingredient_id.protein_g or 0) * scale for ri in recipe_ingredients)
        # total_carbs = sum((ri.ingredient_id.carbs_g or 0) * scale for ri in recipe_ingredients)
        # total_fiber = sum((ri.ingredient_id.fiber_g or 0) * scale for ri in recipe_ingredients)
        # total_saturated_fat_g = sum((ri.ingredient_id.saturated_fat_g or 0) * scale for ri in recipe_ingredients)

        nutrition_list.append({
            'calories': round(total_calories, 1) if total_calories else 'N/A',
            'protein': round(total_protein, 1) if total_protein else 'N/A',
            'carbs': round(total_carbs, 1) if total_carbs else 'N/A',
            'fiber': round(total_fiber, 1) if total_fiber else 'N/A',
            'fats': round(total_saturated_fat_g, 1) if total_saturated_fat_g else 'N/A',
            'adjusted_serving': amount


        })
 
    return render(request, 'recipes/recipes_list.html', {
        'recipes': recipes,
        'recipes_with_nutrition': list(zip(recipes, nutrition_list)),
    })


def recipe_detail(request, recipe_id):
    #from django.shortcuts import get_object_or_404
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

#saving recipes to the user's picked list
@csrf_exempt 
def add_to_picked_recipes(request):
    if request.method == 'POST':
        #if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'You must be logged in to pick recipes'})
        
        try:
            # Parse the JSON data 
            data = json.loads(request.body)
            recipe_title = data.get('recipe_title')
            requested_servings = float(data.get('servings', 1.0))

            user_servings = request.session.get('recipe_servings', {})

            #current_val = user_servings.get(recipe_title, 0.0)
            user_servings[recipe_title] =  requested_servings

            request.session['recipe_servings'] = user_servings
            request.session.modified = True
            
            # check recipe title
            if not recipe_title:
                return JsonResponse({'success': False, 'error': 'Recipe title is required'})
            
    
            # This links Django's User to your custom AppUser model when logged in
            app_user, created = AppUser.objects.get_or_create(user=request.user)
            
            # Get or create UserPickedRecipes for this user, records their picks
            user_picks, created = UserPickedRecipes.objects.get_or_create(user=app_user)
            
            # Parse the existing recipe list
            if user_picks.recipe:
                recipe_list = user_picks.recipe.rstrip("]").split("]")
                recipe_list = [r for r in recipe_list if r]  # Remove empty strings
                #exists = any(entry.split(":")[0] == recipe_title for entry in recipe_list)
            
            else:
                recipe_list = []
            exists = False
            for i, entry in enumerate(recipe_list):
                if entry.split(":")[0] == recipe_title:
                    recipe_list[i]= f"{recipe_title}:{requested_servings}"
                    exists= True
                    break

            if not exists:
                new_serving = f"{recipe_title}:{requested_servings}"
                recipe_list.append(new_serving)

                user_picks.recipe = "]".join(recipe_list) + "]"
                user_picks.save()

            
            #  if recipe is already in the user's picks
            # if recipe_title not in recipe_list:
            #     # Add  new recipe
            #     recipe_list.append(recipe_title)
            #     # Save to database with ] delimiter
            #     user_picks.recipe = "]".join(recipe_list) + "]"
            #     user_picks.save()
                return JsonResponse({'success': True, 'message': f'Added {recipe_title}. Total servings: {user_servings[recipe_title]} to your picks!'})
            else:
                user_picks.recipe = "]".join(recipe_list) + "]"
                user_picks.save()
                return JsonResponse({'success': False, 'error': f'{recipe_title} is already in your picks'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Added recipes page
def selected_recipes(request):
    try:
        app_user = AppUser.objects.get(user=request.user)
        
        user_picks = UserPickedRecipes.objects.get(user=app_user)
    
        if user_picks.recipe:
            recipe_entries= user_picks.recipe.rstrip("]").split("]")
            recipe_entries = [r for r in recipe_entries if r]  # Remove empty strings
        else:
            recipe_entries = []

    except AppUser.DoesNotExist:
        recipe_entries = []
    except UserPickedRecipes.DoesNotExist:
        recipe_entries= []

    final_recipe = []
    nutrition_list = []
    
    for entry in recipe_entries:
        try:
            if ":" in entry:
                title, servings = entry.split(":")
                servings = float(servings)
            else:
                title = entry
                servings = 1.0  # Default fallback

            current_recipe = Recipe.objects.get(title=title)
            
            # Get base nutrition for selected serving size
            recipe_ingredients = Recipe_Ingredients.objects.filter(recipe_id=current_recipe).select_related('ingredient_id')
            base_cal = 0
            base_prot = 0
            base_carb = 0
            base_fiber = 0
            base_fat = 0
        
            for ri in recipe_ingredients:
                factor = float(ri.amount or 0) * servings
                base_cal += (ri.ingredient_id.calories_kcal or 0) * factor
                base_prot += (ri.ingredient_id.protein_g or 0) * factor
                base_carb += (ri.ingredient_id.carbs_g or 0) * factor
                base_fiber += (ri.ingredient_id.fiber_g or 0) * factor
                base_fat += (ri.ingredient_id.saturated_fat_g or 0) * factor
            # recipe_ingredients = Recipe_Ingredients.objects.filter(recipe_id=current_recipe.id).select_related('ingredient_id')
            
            # base_cal = sum(ri.ingredient_id.calories_kcal or 0 for ri in recipe_ingredients)
            # base_prot = sum(ri.ingredient_id.protein_g or 0 for ri in recipe_ingredients)
            # base_carb = sum(ri.ingredient_id.carbs_g or 0 for ri in recipe_ingredients)
            # base_fiber = sum(ri.ingredient_id.fiber_g or 0 for ri in recipe_ingredients)
            # base_fat = sum(ri.ingredient_id.saturated_fat_g or 0 for ri in recipe_ingredients)

            # Multiplies by the saved servings
            nutrition_list.append({
                'calories': round(base_cal, 1),
                'protein': round(base_prot, 1),
                'carbs': round(base_carb, 1),
                'fiber': round(base_fiber, 1),
                'fats': round(base_fat, 1),
                'applied_servings': servings # Pass this to show on the page
            })
            
            final_recipe.append(current_recipe)

        except Recipe.DoesNotExist:
            continue
    
    return render(request, 'recipes/selected_recipes.html', {
        "recipes_with_nutrition": zip(final_recipe, nutrition_list)
    })

def remove_recipes(request):
    try:
        app_user = AppUser.objects.get(user=request.user)
        user_picks = UserPickedRecipes.objects.get(user=app_user)

        data = json.loads(request.body)
        recipe_title = data.get('recipe_title')

        if user_picks.recipe:
            recipe_list = [r for r in user_picks.recipe.rstrip("]").split("]") if r]

            # Keeps everything except the recipe matching the title
            recipe_list = [r for r in recipe_list if r.split(":")[0] != recipe_title]
        
            user_picks.recipe = "]".join(recipe_list) + "]" if recipe_list else ""
            user_picks.save()
    
        return JsonResponse({'success': True, 'message': f'Removed {recipe_title} from your picks!'})
    
    #     if user_picks.recipe:
    #         recipe_list = user_picks.recipe.rstrip("]").split("]")
    #         recipe_list = [r for r in recipe_list if r]  # Remove empty strings
    #     else:
    #         recipe_list = []

    except (AppUser.DoesNotExist,UserPickedRecipes.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'User profile or picks not found'})
    except Exception as e :
        return JsonResponse({'success': False, 'error': str(e)})

    # data = json.loads(request.body)
    # recipe_title = data.get('recipe_title')

    # if recipe_title in recipe_list:
    #     recipe_list.remove(recipe_title)
        
    # user_picks.recipe = "]".join(recipe_list) + "]"
    
    # user_picks.save()
    # return JsonResponse({'success': True, 'message': f'Removed {recipe_title} from your picks!'})

# Forgot password page
def forgot_password_page(request):
    error_info = {"errors": {}, "email": "", "sent": False}

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        error_info["email"] = email

        if not email:
            error_info["errors"]["email"]= "Email is required"
        else:
            try:
                validate_email(email)
            except ValidationError:
                error_info["errors"]["email"] = "Not a valid email address"
            
            send_mail(
                subject= "Eatilligent Forgotten Password",
                message= "This email is for your forgotten password",
                from_email=EMAIL_HOST_USER,
                recipient_list= [email],
            )          
            error_info["sent"] = True     
    return render(request, "main/forgotpass.html", error_info)



@login_required
def user_profile(request):
    app_user = get_object_or_404(AppUser, user=request.user)
    all_diseases = Disease.objects.all().order_by('title')
    user_picks, created = UserPickedDisease.objects.get_or_create(user=app_user)

    if request.method == 'POST':
        # Capture the new selection from the dropdown for diseases
        new_disease_title = request.POST.get('disease')
        
        # Current disease user input
        current_badge_titles = request.POST.getlist('active_diseases')

        # Combines added disease and old diseasinto a single list
        updated_title_list = list(set(current_badge_titles))
        if new_disease_title and new_disease_title not in updated_title_list:
            updated_title_list.append(new_disease_title)

        disease_objects = Disease.objects.filter(title__in=updated_title_list)
        app_user.diseases.set(disease_objects)

        final_titles = [d.title for d in disease_objects]
        user_picks.disease = "]".join(final_titles) + "]" if final_titles else ""

        # Saves user info
        app_user.weight = request.POST.get('weight') or app_user.weight
        app_user.height = request.POST.get('height') or app_user.height
        app_user.age = request.POST.get('age') or app_user.age
        app_user.gender = request.POST.get('gender')
        app_user.activity_level = request.POST.get('activity_level')

        restrictions_list = request.POST.getlist('dietary_restrictions')
        app_user.dietary_restriction = ", ".join(restrictions_list)
        
        app_user.save()
        user_picks.save()
        
        return redirect('user_profile')

    # Parses through disease list
    picked_diseases = [d for d in user_picks.disease.rstrip("]").split("]") if d]

    return render(request, 'recipes/userprofile.html', {
        'app_user': app_user,
        'all_diseases': all_diseases,
        'picked_diseases': picked_diseases,
    })

def disease_page(request):
    if not request.user.is_authenticated:
        return redirect("login_page")
    
    diseases = Disease.objects.prefetch_related(
        "disease_super_food_set__ingredient_id",
        "disease_avoid_food_set__ingredient_id"
    )
    return render(request, "main/disease_page.html",{
        "diseases": diseases
    })


def disease_detail(request, id):
    if not request.user.is_authenticated:
        return redirect("login_page")
    
    diseases = Disease.objects.prefetch_related(
        "disease_super_food_set__ingredient_id",
        "disease_avoid_food_set__ingredient_id"
    ).get(id=id)

    return render(request, "main/disease_detail.html",{
        "diseases": diseases
    })


def grocery_list(request):
    try:
        app_user = AppUser.objects.get(user=request.user)
        
        user_picks = UserPickedRecipes.objects.get(user=app_user)
    
        if user_picks.recipe:
            recipe_list = user_picks.recipe.rstrip("]").split("]")
            recipe_list = [r for r in recipe_list if r]  # Remove empty strings
        else:
            recipe_list = []

    except AppUser.DoesNotExist:
        recipe_list = []
    except UserPickedRecipes.DoesNotExist:
        recipe_list = []

    ingredients_amount = {}
    

    for entry in recipe_list:
        try:    
            if ":" in entry:
                r_title, multiply = entry.split(":")
                multiply = float(multiply)
            else:
                r_title = entry
                multiply = 1.0

            current_recipe = Recipe.objects.get(title=r_title)
            recipe_ingredient_list = Recipe_Ingredients.objects.filter(recipe_id=current_recipe.id)

            for link in recipe_ingredient_list:
                current_ingredient = link.ingredient_id 
                base_amount = float(link.amount) if link.amount else 0
                unit_val = float(current_ingredient.measurement_amount) if current_ingredient.measurement_amount else 1
                new_amount = base_amount * unit_val * float(multiply)
                if current_ingredient not in ingredients_amount:
                    ingredients_amount[current_ingredient] = new_amount
                else:
                    ingredients_amount[current_ingredient] += new_amount
        except Recipe.DoesNotExist:
            continue
    

    return render(request, 'recipes/grocerylist.html', {"recipes": recipe_list, "ingredients": ingredients_amount})

# took the format for saving recipes to the user's picked list to create it for diseases with the same functionality
@csrf_exempt 
def add_to_picked_disease(request):
    if request.method == 'POST':
        #if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'You must be logged in to pick a disease'})
        
        try:
            # Parse the JSON data 
            data = json.loads(request.body)
            disease_title = data.get('disease_title')
            
            # check recipe title
            if not disease_title:
                return JsonResponse({'success': False, 'error': 'Disease title is required'})
            
            # Get or create AppUser for the logged-in user
            # This links Django's User to your custom AppUser model
            app_user, created = AppUser.objects.get_or_create(user=request.user)
            
            # Get or create UserPickedDisease for this user
            # Each user has one UserPickedDisease record with all their picks
            user_picks, created = UserPickedDisease.objects.get_or_create(user=app_user)
            
            # Parse the existing recipe list from the TextField
            # Format is: "Recipe1]Recipe2]Recipe3]"
            if user_picks.disease:
                disease_list = user_picks.disease.rstrip("]").split("]")
                disease_list = [d for d in disease_list if d]  # Remove empty strings
            else:
                disease_list = []
            
            #  if disease is already in the user's picks
            if disease_title not in disease_list:
                # Add  new disease
                disease_list.append(disease_title)
                # Save to database with ] delimiter
                user_picks.disease = "]".join(disease_list) + "]"
                user_picks.save()
                return JsonResponse({'success': True, 'message': f'Added {disease_title} to your profile!'})
            else:
                return JsonResponse({'success': False, 'error': f'{disease_title} is already in your profile'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Added disease page
def selected_disease(request):
    try:
        app_user = AppUser.objects.get(user=request.user)
        
        user_picks = UserPickedDisease.objects.get(user=app_user)
    
        if user_picks.disease:
            disease_list = user_picks.disease.rstrip("]").split("]")
            disease_list = [d for d in disease_list if d]  # Remove empty strings
            disease_list = Disease.objects.filter(title__in=disease_list)
        else:
            disease_list= []

    except AppUser.DoesNotExist:
        disease_list = []
    except UserPickedDisease.DoesNotExist:
        disease_list = []

    return render(request, 'main/selected_disease.html', {"disease": disease_list})

def custom_user_recipe(request):
    error_info = {"errors": {}}

    if request.method == "POST":
        title = request.POST.get('title')
        mealType = request.POST.getlist('type')
        ingredientList = [i.strip() for i in request.POST.getlist('ingredient-selection') if i.strip()]
        amountsList = [a.strip() for a in request.POST.getlist('ingredient-amount') if a.strip()]
        instructions = request.POST.get('instructions')



        if Recipe.objects.filter(title=title):
            error_info["errors"]["title"] = "Recipe with that name already exists"

        if not title:
            error_info["errors"]["title"] = "Title is required"
        
        
        
        if not mealType:
            error_info["errors"]["type"] = "Select at least one meal type"

        if not ingredientList:
            error_info["errors"]["ingredients"] = "Ingredient cannot be empty (input ingredient or remove field)"

        if not amountsList or len(amountsList) != len(ingredientList):
            error_info["errors"]["amounts"] = "Amount is required for all ingredients"

        if not instructions or instructions.strip() == "":
            error_info["errors"]["instructions"] = "Cooking instructions are required"

        if not error_info["errors"]:
            newId = 1
            while newId in Recipe.objects.values_list("id", flat=True):
                newId += 1

            mealType = "; ".join(mealType)
            ingredientListString = ";".join(ingredientList)

            Recipe.objects.create(
                id = newId,
                title = title,
                meal_type = mealType,
                ingredients = ingredientListString,
                how_to_cook = instructions
            )

            for i,a in list(zip(ingredientList, amountsList)):
                current_ingredient_id = Ingredient.objects.filter(title=i).first().id
                Recipe_Ingredients.objects.create(
                    recipe_id = Recipe.objects.get(id=newId),
                    ingredient_id = Ingredient.objects.get(id=current_ingredient_id),
                    amount = a
                )
            
            return redirect('recipes_list')

    ingredients = Ingredient.objects.all()
    return render(request, 'recipes/customrecipe.html', {'ingredients':ingredients, "errors": error_info['errors']})

def weekly_digest(request):
    if not request.user.is_authenticated:
        return redirect("login_page")
    
    if request.user.is_authenticated:
        try:
            app_user = AppUser.objects.get(user=request.user)

            try:
                user_picks = UserPickedDisease.objects.get(user=app_user)
                picked_disease = [d for d in user_picks.disease.rstrip("]").split("]") if d]
                user_disease_ids = Disease.objects.filter(title__in=picked_disease).values_list('id', flat=True)
            except UserPickedDisease.DoesNotExist:
                user_disease_ids = []

            avoid_ingredient_ids = Disease_Avoid_Food.objects.filter(
                disease_id__in=user_disease_ids
            ).values_list('ingredient_id', flat=True)

            if avoid_ingredient_ids:
                avoided_recipe_ids = Recipe_Ingredients.objects.filter(
                    ingredient_id__in=avoid_ingredient_ids
                ).values_list('recipe_id', flat=True)
                recipes = list(Recipe.objects.all().order_by('title').exclude(id__in=avoided_recipe_ids))

        except AppUser.DoesNotExist:
            pass
    my_recipies = Recipe.objects.filter(id__in=UserPickedRecipes.objects.filter(user=app_user).values_list('recipe', flat=True))

    # Build nutrition list — always runs, same size/order as recipes
    nutrition_list = []
    highest_cal = 0
    lowest_cal = float('inf')
    highest_cal_recipe = None
    lowest_cal_recipe = None
    for recipe in recipes:
        recipe_ingredients = Recipe_Ingredients.objects.filter(recipe_id=recipe).select_related('ingredient_id')
        total_calories = sum(ri.ingredient_id.calories_kcal or 0 for ri in recipe_ingredients)
        total_protein = sum(ri.ingredient_id.protein_g or 0 for ri in recipe_ingredients)
        total_carbs = sum(ri.ingredient_id.carbs_g or 0 for ri in recipe_ingredients)
        nutrition_list.append({
            'calories': round(total_calories, 1) if total_calories else 'N/A',
            'protein': round(total_protein, 1) if total_protein else 'N/A',
            'carbs': round(total_carbs, 1) if total_carbs else 'N/A',
        })
        if total_calories > highest_cal:
            highest_cal = total_calories
            highest_cal_recipe = recipe
        if total_calories < lowest_cal:
            lowest_cal = total_calories
            lowest_cal_recipe = recipe
        
    not_Chosen= Recipe.objects.all().exclude(title__in=[r for r in recipes])
    random_recipe = random.choice(not_Chosen) if not_Chosen else None


    ingredient_count = {}
    for recipe in recipes:
        recipe_ingredients = Recipe_Ingredients.objects.filter(recipe_id=recipe).select_related('ingredient_id')
        for ri in recipe_ingredients:
            ingredient_title = ri.ingredient_id.title
            if ingredient_title not in ingredient_count:
                ingredient_count[ingredient_title] = 1
            else:
                ingredient_count[ingredient_title] += 1

    # Get most common ingredient
    most_common_ingredient = max(ingredient_count, key=ingredient_count.get) if ingredient_count else None

    sevenDaysAgo = date.today() - timedelta(days=6)
    results = DailyLog.objects.all().filter(user=request.user)
    results = results.filter(date__gte=sevenDaysAgo)
    sevenDaysAgoLst = [date.today() - timedelta(days=i) for i in range(7)]

    results_json = json.dumps([
        {
            'date': str(log.date),
            'total_calories': log.total_calories,
            'total_protein': log.total_protein,
            'total_carbs': log.total_carbs,
            'total_fats': log.total_fats,
            'net_calories': log.net_calories,
        }
        for log in results
    ])
    
    myWorkouts= WorkoutEntry.objects.filter(daily_log__in=results)
    mydict = {str(date): 0 for date in sevenDaysAgoLst}
    for w in myWorkouts:
        date_str = str(w.daily_log.date)
        if date_str in mydict:
            mydict[date_str] += 1


    workouts_json = json.dumps({str(k): v for k, v in mydict.items()})



    return render(request, 'recipes/weekly_digest.html', {
        'recipes': recipes,
        'recipes_with_nutrition': list(zip(recipes, nutrition_list)),
        'most_common_ingredient': most_common_ingredient,
        'highest_cal_recipe': highest_cal_recipe,
        'not_Chosen': random_recipe,
        'lowest_cal_recipe': lowest_cal_recipe,
        'highest_cal': round(highest_cal, 1),
        'lowest_cal': round(lowest_cal, 1),
        'results_json': results_json,
        'workouts_json': workouts_json,
    })





@login_required
def daily_digest(request):
    """
    Display the daily nutrition digest page with personalized meal slots
    """
    from recipes.models import Quote, Recipe, AppUser
    import random
    
    # Get random quote
    quotes = Quote.objects.all()
    quote = random.choice(list(quotes)) if quotes.exists() else None
    
    # Get AppUser instance
    try:
        app_user = AppUser.objects.get(user=request.user)
        meals_per = app_user.meals_per or 3  # Default to 3 meals
        snacks_per = app_user.snacks_per or 1  # Default to 1 snack
    except AppUser.DoesNotExist:
        meals_per = 3
        snacks_per = 1
    
    # Get all recipes from the database
    # (Since UserPickedRecipes doesn't have a proper relationship, just get all recipes)
    user_recipe_list = Recipe.objects.all()[:50]  # Limit to 50 for performance
    
    context = {
        'quote': quote,
        'meal_range': range(meals_per),
        'snack_range': range(snacks_per) if snacks_per > 0 else None,
        'user_recipes': user_recipe_list
    }
    
    return render(request, 'recipes/daily_digest.html', context)
@login_required
@require_http_methods(["GET"])
def get_daily_data(request):
    """
    API endpoint to get today's daily log data
    """
    today = date.today()
    app_user = AppUser.objects.get(user=request.user)
    
    # Get or create today's log
    daily_log, created = DailyLog.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'calorie_goal': app_user.calorie_goal or 2000} #gets user set goal or default of 2000
    )
    
    # Get all meals for today
    meals = list(daily_log.meals.values(
        'id', 'meal_name', 'calories', 'protein', 'carbs', 'fats', 'logged_at'
    ))
    
    # Get all workouts for today
    workouts = list(daily_log.workouts.values(
        'id', 'workout_type', 'calories_burned', 'logged_at'
    ))
    
    return JsonResponse({
        'success': True,
        'date': str(today),
        'total_calories': daily_log.total_calories,
        'total_protein': daily_log.total_protein,
        'total_carbs': daily_log.total_carbs,
        'total_fats': daily_log.total_fats,
        'total_burned': daily_log.total_burned,
        'calorie_goal': daily_log.calorie_goal,
        'net_calories': daily_log.net_calories,
        'remaining_calories': daily_log.remaining_calories,
        'meals': meals,
        'workouts': workouts,
    })


@login_required
@require_http_methods(["POST"])
def add_meal(request):
    """
    API endpoint to add a meal entry
    """
    try:
        data = json.loads(request.body)
        today = date.today()
        app_user = AppUser.objects.get(user=request.user)
        
        # Get or create today's log
        daily_log, created = DailyLog.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'calorie_goal': app_user.calorie_goal or 2000} #gets user set goal or default of 2000
    )
        
        # Create meal entry
        meal = MealEntry.objects.create(
            daily_log=daily_log,
            meal_name=data.get('meal_name', 'Meal'),
            calories=float(data.get('calories', 0)),
            protein=float(data.get('protein', 0)),
            carbs=float(data.get('carbs', 0)),
            fats=float(data.get('fats', 0)),
        )
        
        # Update daily totals
        daily_log.total_calories += meal.calories
        daily_log.total_protein += meal.protein
        daily_log.total_carbs += meal.carbs
        daily_log.total_fats += meal.fats
        daily_log.save()
        
        return JsonResponse({
            'success': True,
            'meal_id': meal.id,
            'total_calories': daily_log.total_calories,
            'total_protein': daily_log.total_protein,
            'total_carbs': daily_log.total_carbs,
            'total_fats': daily_log.total_fats,
            'net_calories': daily_log.net_calories,
            'remaining_calories': daily_log.remaining_calories,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def add_workout(request):
    """
    API endpoint to add a workout entry
    """
    try:
        data = json.loads(request.body)
        today = date.today()
        app_user = AppUser.objects.get(user=request.user)
        
        # Get or create today's log
        daily_log, created = DailyLog.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'calorie_goal': app_user.calorie_goal or 2000} #gets user set goal or default of 2000
        )
        
        # Create workout entry
        workout = WorkoutEntry.objects.create(
            daily_log=daily_log,
            workout_type=data.get('workout_type', 'other'),
            calories_burned=float(data.get('calories_burned', 0)),
        )
        
        # Update daily totals
        daily_log.total_burned += workout.calories_burned
        daily_log.save()
        
        return JsonResponse({
            'success': True,
            'workout_id': workout.id,
            'total_burned': daily_log.total_burned,
            'net_calories': daily_log.net_calories,
            'remaining_calories': daily_log.remaining_calories,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    


def recipe_info(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    recipe_ingredient_list = Recipe_Ingredients.objects.filter(recipe_id=recipe.id).select_related('ingredient_id')
    #multi = request.GET.get('servings', 1)
    servings = 1.0
    
    if request.user.is_authenticated:
        try:
            app_user = AppUser.objects.get(user=request.user)
            user_picks = UserPickedRecipes.objects.get(user=app_user)
            
            if user_picks.recipe:
                # Split the string: "Apple Cinnamon Oatmeal:2.0, Other Recipe:1.0"
                entries = [e for e in user_picks.recipe.rstrip("]").split("]") if e]
                for entry in entries:
                    if ":" in entry:
                        name, serv = entry.split(":")
                        if name == recipe.title:
                            servings = float(serv)
                            break
        except (AppUser.DoesNotExist, UserPickedRecipes.DoesNotExist):
            pass
    
    instructions = recipe.how_to_cook
    instruction_list = re.split(r'\d+\.\s', instructions.strip('"'))[1:]
    ingredient_list = []
    amount_list = []

    # for i in recipe_ingredient_list:
    #     ingredient_list.append(i.ingredient_id)


        
    total_calories=0
    total_protein=0
    total_carbs=0
    total_fiber=0
    total_saturated_fat_g=0
    Sugar_g = 0
    cholesterol_mg = 0
    sodium_mg = 0
    potassium_mg = 0
    Iron_mg = 0
    Calcium_mg = 0
    Phosphorus_mg = 0
    magnesium_mg = 0
    Vitamin_A_ug = 0
    vitamin_b_mg = 0
    Vitamin_C_mg = 0
    Vitamin_D_ug = 0
    Vitamin_E_mg = 0
    Vitamin_K_ug = 0
    Zinc_mg = 0
    Iodine_ug = 0
    Selenium_ug = 0
    Copper_mg = 0
    Fluoride_mg = 0
    Chromium_mg = 0

    for i in recipe_ingredient_list:
        ingredient = i.ingredient_id
        factor = float(i.amount or 0) * servings

        # Adjusts measurements for given serving
        actual_amount = factor * float(ingredient.measurement_amount or 1) 
        ingredient_list.append(ingredient)
        amount_list.append(actual_amount)

    # multiply = float(request.GET.get('multi', 1))
    # qSetofingredients = Recipe_Ingredients.objects.filter(recipe_id=recipe.id).select_related('ingredient_id')
    # for i in qSetofingredients:
        # Calculates updated nutritional info to the updated serving size selected
        total_calories += (i.ingredient_id.calories_kcal or 0) * factor
        total_protein += (i.ingredient_id.protein_g or 0) * factor
        total_carbs += (i.ingredient_id.carbs_g or 0) * factor
        total_fiber += (i.ingredient_id.fiber_g or 0) * factor
        total_saturated_fat_g += (i.ingredient_id.saturated_fat_g or 0) * factor
        Sugar_g += (i.ingredient_id.sugar_g or 0) * factor
        cholesterol_mg += (i.ingredient_id.cholesterol_mg or 0) * factor
        sodium_mg += (i.ingredient_id.sodium_mg or 0) * factor
        potassium_mg += (i.ingredient_id.potassium_mg or 0) * factor
        Iron_mg += (i.ingredient_id.iron_mg or 0) * factor
        Calcium_mg += (i.ingredient_id.calcium_mg or 0) * factor
        Phosphorus_mg += (i.ingredient_id.phosphorus_mg or 0) * factor
        magnesium_mg += (i.ingredient_id.magnesium_mg or 0) * factor
        Vitamin_A_ug += (i.ingredient_id.vitamin_a_ug or 0) * factor
        vitamin_b_mg += (i.ingredient_id.vitamin_b_mg or 0) * factor
        Vitamin_C_mg += (i.ingredient_id.vitamin_c_mg or 0) * factor
        Vitamin_D_ug += (i.ingredient_id.vitamin_d_ug or 0) * factor
        Vitamin_E_mg += (i.ingredient_id.vitamin_e_mg or 0) * factor
        Vitamin_K_ug += (i.ingredient_id.vitamin_k_ug or 0) * factor
        Zinc_mg += (i.ingredient_id.zinc_mg or 0) * factor
        Iodine_ug += (i.ingredient_id.iodine_ug or 0) * factor
        Selenium_ug += (i.ingredient_id.selenium_ug or 0) * factor
        Copper_mg += (i.ingredient_id.copper_mg or 0) * factor
        Fluoride_mg += (i.ingredient_id.fluoride_mg or 0) * factor
        Chromium_mg += (i.ingredient_id.chromium_mg or 0) * factor

    dictionaryOfNutritionFacts = {
        'calories': round(total_calories, 1) if total_calories else 'N/A',
        'protein': round(total_protein, 1) if total_protein else 'N/A',
        'carbs': round(total_carbs, 1) if total_carbs else 'N/A',
        'fiber': round(total_fiber, 1) if total_fiber else 'N/A',
        'fats': round(total_saturated_fat_g, 1) if total_saturated_fat_g else 'N/A',
        'Sugar_g': round(Sugar_g, 1) if Sugar_g else 'N/A',
        'cholesterol_mg': round(cholesterol_mg, 1) if cholesterol_mg else 'N/A',
        'sodium_mg': round(sodium_mg, 1) if sodium_mg else 'N/A',
        'potassium_mg': round(potassium_mg, 1) if potassium_mg else 'N/A',
        'Iron_mg': round(Iron_mg, 1) if Iron_mg else 'N/A',
        'Calcium_mg': round(Calcium_mg, 1) if Calcium_mg else 'N/A',
        'Phosphorus_mg': round(Phosphorus_mg, 1) if Phosphorus_mg else 'N/A',
        'magnesium_mg': round(magnesium_mg, 1) if magnesium_mg else 'N/A',
        'Vitamin_A_ug': round(Vitamin_A_ug, 1) if Vitamin_A_ug else 'N/A',
        'vitamin_b_mg': round(vitamin_b_mg, 1) if vitamin_b_mg else 'N/A',
        'Vitamin_C_mg': round(Vitamin_C_mg, 1) if Vitamin_C_mg else 'N/A',
        'Vitamin_D_ug': round(Vitamin_D_ug, 1) if Vitamin_D_ug else 'N/A',
        'Vitamin_E_mg': round(Vitamin_E_mg, 1) if Vitamin_E_mg else 'N/A',
        'Vitamin_K_ug': round(Vitamin_K_ug, 1) if Vitamin_K_ug else 'N/A',
        'Zinc_mg': round(Zinc_mg, 1) if Zinc_mg else 'N/A',
        'Iodine_ug': round(Iodine_ug, 1) if Iodine_ug else 'N/A',
        'Selenium_ug': round(Selenium_ug, 1) if Selenium_ug else 'N/A',
        'Copper_mg': round(Copper_mg, 1) if Copper_mg else 'N/A',
        'Fluoride_mg': round(Fluoride_mg, 1) if Fluoride_mg else 'N/A',
        'Chromium_mg': round(Chromium_mg, 1) if Chromium_mg else 'N/A'
    }

    
    # amount_list = []

    # for i in recipe_ingredient_list:
    #     ingredient_list.append(i.ingredient_id)
    #     amount_list.append(i.amount)





    return render(request,'recipes/recipe_info.html', {
        "recipe": recipe, "ingredients": list(zip(ingredient_list, amount_list)), 
        "instructions": instruction_list, "nutrition": dictionaryOfNutritionFacts,
        "multi":servings
        })    
@login_required
def goals_page(request):
    app_user = AppUser.objects.get(user=request.user)
    diseases = app_user.diseases.all()
    active_goals = Goal.objects.filter(user=app_user, is_active=True).order_by("-created_at")
    completed_goals = Goal.objects.filter(user=app_user, completed=True, is_active=False).order_by('-completed_at')
    edit_goal = None
    recent_weight_entries = WeightEntry.objects.filter(user=app_user)[:5]

    default_calories = None
    default_carbs = None
    default_protein = None
    default_fat = None

    high_calories = None
    high_carbs = None
    high_protein = None
    high_fat = None

    # determines reccomennded ranges based on all the selected diseases
    if diseases.exists():
        #gets low vals for reccommended ranges
        low_calories_values = [d.low_calories_kcal for d in diseases if d.low_calories_kcal is not None]
        low_carbs_values = [d.low_carbs_g for d in diseases if d.low_carbs_g is not None]
        low_protein_values = [d.low_protein_g for d in diseases if d.low_protein_g is not None]
        low_fat_values = [d.low_saturated_fat_g for d in diseases if d.low_saturated_fat_g is not None]

        #gets high vals for reccommended ranges
        high_calories_values = [d.high_calories_kcal for d in diseases if d.high_calories_kcal is not None]
        high_carbs_values = [d.high_carbs_g for d in diseases if d.high_carbs_g is not None]
        high_protein_values = [d.high_protein_g for d in diseases if d.high_protein_g is not None]
        high_fat_values = [d.high_saturated_fat_g for d in diseases if d.high_saturated_fat_g is not None]

        #calculates the overlap range for nutritional values based on the selected diseases
        overlap_low_calories = max(low_calories_values) if low_calories_values else None
        overlap_low_carbs = max(low_carbs_values) if low_carbs_values else None
        overlap_low_protein = max(low_protein_values) if low_protein_values else None
        overlap_low_fat = max(low_fat_values) if low_fat_values else None

        overlap_high_calories = min(high_calories_values) if high_calories_values else None
        overlap_high_carbs = min(high_carbs_values) if high_carbs_values else None
        overlap_high_protein = min(high_protein_values) if high_protein_values else None
        overlap_high_fat = min(high_fat_values) if high_fat_values else None

        #calculates average ranges based on the selected diseases if the overlap ranges show conflicting values (ex: overlap_low_calories is higher than overlap_high_calories)
        avg_low_calories = sum(low_calories_values) / len(low_calories_values) if low_calories_values else None
        avg_low_carbs = sum(low_carbs_values) / len(low_carbs_values) if low_carbs_values else None
        avg_low_protein = sum(low_protein_values) / len(low_protein_values) if low_protein_values else None
        avg_low_fat = sum(low_fat_values) / len(low_fat_values) if low_fat_values else None

        avg_high_calories = sum(high_calories_values) / len(high_calories_values) if high_calories_values else None
        avg_high_carbs = sum(high_carbs_values) / len(high_carbs_values) if high_carbs_values else None
        avg_high_protein = sum(high_protein_values) / len(high_protein_values) if high_protein_values else None
        avg_high_fat = sum(high_fat_values) / len(high_fat_values) if high_fat_values else None

        #uses the overlap range if it is valid, otherwise the average range is used as an alternative recommendation
        if overlap_low_calories is not None and overlap_high_calories is not None and overlap_low_calories <= overlap_high_calories:
            default_calories = overlap_low_calories
            high_calories = overlap_high_calories
        else:
            default_calories = avg_low_calories
            high_calories = avg_high_calories

        if overlap_low_carbs is not None and overlap_high_carbs is not None and overlap_low_carbs <= overlap_high_carbs:
            default_carbs = overlap_low_carbs
            high_carbs = overlap_high_carbs
        else:
            default_carbs = avg_low_carbs
            high_carbs = avg_high_carbs

        if overlap_low_protein is not None and overlap_high_protein is not None and overlap_low_protein <= overlap_high_protein:
            default_protein = overlap_low_protein
            high_protein = overlap_high_protein
        else:
            default_protein = avg_low_protein
            high_protein = avg_high_protein
        
        if overlap_low_fat is not None and overlap_high_fat is not None and overlap_low_fat <= overlap_high_fat:
            default_fat = overlap_low_fat
            high_fat = overlap_high_fat
        else:
            default_fat = avg_low_fat
            high_fat = avg_high_fat






    if request.method == "POST":
        action = request.POST.get("action")

        #marks custom goal as completed
        if action == "complete_goal":
            goal_id = request.POST.get("goal_id")
            try:
                goal = Goal.objects.get(id=goal_id, user=app_user)
                goal.completed = True
                goal.completed_at = timezone.now()
                goal.is_active = False
                goal.save()
                messages.success(request, "Goal marked as completed!")
            except Goal.DoesNotExist:
                messages.error(request, "Goal not found.")
            return redirect('goals_page')
        elif action == "reactivate_goal":
            goal_id = request.POST.get("goal_id")
            try:
                goal = Goal.objects.get(id=goal_id, user=app_user)
                goal.completed = False
                goal.completed_at = None
                goal.is_active = True
                goal.save()
                messages.success(request, "Goal reactivated!")
            except Goal.DoesNotExist:
                messages.error(request, "Goal not found.")
            return redirect('goals_page')
        
        # creates a new custom goal
        elif action == "create_custom_goal":
            goal_name = request.POST.get("goal_name")
            goal_description = request.POST.get("goal_description")
            goal_target_value = request.POST.get("goal_target_value")
            goal_time_period = request.POST.get("time_period")
            goal_unit = request.POST.get("unit")

            if goal_name:
                Goal.objects.create(
                    user=app_user,
                    name=goal_name,
                    description=goal_description,
                    target_value=goal_target_value if goal_target_value else None,
                    time_period=goal_time_period if goal_time_period else None,
                    completed=False,
                    is_active=True,
                    unit=goal_unit if goal_unit else None,
                )
                messages.success(request, "Custom goal created successfully!")
            else:
                messages.error(request, "Goal name is required to create a custom goal.")
            return redirect('goals_page')
        elif action == "delete_goal":
            goal_id = request.POST.get("goal_id")

            try:
                goal = Goal.objects.get(id=goal_id, user=app_user)
                goal.delete()
                messages.success(request, "Goal deleted successfully!")
            except Goal.DoesNotExist:
                messages.error(request, "Goal not found.")
        elif action == "delete_weight_entry":
            entry_id = request.POST.get("entry_id")
            try:
                entry = WeightEntry.objects.get(id=entry_id, user=app_user)
                entry.delete()
                messages.success(request, "Weight entry deleted successfully!")
            except WeightEntry.DoesNotExist:
                messages.error(request, "Weight entry not found.")

            return redirect('goals_page')
        elif action == "start_edit_goal":
            goal_id = request.POST.get("goal_id")
            

            try:
                edit_goal = Goal.objects.get(id=goal_id, user=app_user, is_active=True)
            except Goal.DoesNotExist:
                messages.error(request, "Goal not found.")
        elif action == "edit_goal":
            goal_id = request.POST.get("goal_id")

            try:
                goal = Goal.objects.get(id=goal_id, user=app_user, is_active=True)
                goal_name = request.POST.get("goal_name")
                goal_description = request.POST.get("goal_description")
                goal_target_value = request.POST.get("goal_target_value")
                goal_time_period = request.POST.get("time_period")
                goal_unit = request.POST.get("unit")

                if goal_name:
                    goal.name = goal_name
                    goal.description = goal_description
                    goal.target_value = goal_target_value if goal_target_value else None
                    goal.time_period = goal_time_period if goal_time_period else None
                    goal.unit = goal_unit if goal_unit else None
                    goal.save()
                    messages.success(request, "Goal updated successfully!")
                else:
                    messages.error(request, "Goal name is required.")

            except Goal.DoesNotExist:
                messages.error(request, "Goal not found.")

            return redirect('goals_page')
        
        # update nutrition/activity/weight goals
        else:
            calorie_goal = request.POST.get("calorie_goal")
            carb_goal = request.POST.get("carb_goal")
            protein_goal = request.POST.get("protein_goal")
            fat_goal = request.POST.get("fat_goal")
            current_weight = request.POST.get("weight")
            goal_weight = request.POST.get("goal_weight")
            activity_level = request.POST.get("activity_level")
            weight_goal_type = request.POST.get("weight_goal_type")

            app_user.calorie_goal = calorie_goal or default_calories
            app_user.carb_goal = carb_goal or default_carbs
            app_user.protein_goal = protein_goal or default_protein
            app_user.fat_goal = fat_goal or default_fat
            app_user.goal_weight = goal_weight or app_user.goal_weight
            app_user.activity_level = activity_level or app_user.activity_level
            weight_goal_type = (request.POST.get("weight_goal_type") or "").strip()
            valid_goal_types = {k for k, _ in AppUser.WEIGHT_GOAL_CHOICES}

            if weight_goal_type in valid_goal_types:
                app_user.weight_goal_type = weight_goal_type
            elif weight_goal_type == "":
                app_user.weight_goal_type = None
                
            try:
                if current_weight:
                    current_weight_value = float(current_weight)
                    #checks if user has previous weight entries
                    has_prev_entry = WeightEntry.objects.filter(user=app_user).exists()
                    #record weight entry if it is their first one or if their weight changed
                    if not has_prev_entry or app_user.weight != current_weight_value:
                        app_user.weight = current_weight_value
                        WeightEntry.objects.create(user=app_user, weight=current_weight_value)
            except ValueError:
                messages.error(request, "Please enter a valid number for weight.")
                return redirect('goals_page')
            app_user.save()

            warnings = []

            try:
                if app_user.calorie_goal is not None and high_calories is not None and float(app_user.calorie_goal)>float(high_calories):
                    warnings.append(f"Your calorie goal of {app_user.calorie_goal} kcal exceeds the recommended maximum of {high_calories} kcal for your condition.")
                if app_user.carb_goal is not None and high_carbs is not None and float(app_user.carb_goal)>float(high_carbs):
                    warnings.append(f"Your carbohydrate goal of {app_user.carb_goal} g exceeds the recommended maximum of {high_carbs} g for your condition.")
                if app_user.protein_goal is not None and high_protein is not None and float(app_user.protein_goal)>float(high_protein):
                    warnings.append(f"Your protein goal of {app_user.protein_goal} g exceeds the recommended maximum of {high_protein} g for your condition.")
                if app_user.fat_goal is not None and high_fat is not None and float(app_user.fat_goal)>float(high_fat):
                    warnings.append(f"Your fat goal of {app_user.fat_goal} g exceeds the recommended maximum of {high_fat} g for your condition.")
            except ValueError:
                messages.error(request, "Please enter valid numeric values for goals.")
                return redirect('goals_page')
            if warnings:
                for warning in warnings:
                    messages.warning(request, warning)
            else:
                messages.success(request, "Goals updated successfully!")
            return redirect('goals_page')

       
    
    context = {
        "app_user": app_user,
        "default_calories": default_calories,
        "default_carbs": default_carbs,
        "default_protein": default_protein,
        "default_fat": default_fat,
        "high_calories": high_calories,
        "high_carbs": high_carbs,
        "high_protein": high_protein,
        "high_fat": high_fat,
        "active_goals": active_goals,
        "completed_goals": completed_goals,
        "edit_goal": edit_goal,
        "recent_weight_entries": recent_weight_entries,
    }
    return render(request, 'recipes/goals.html', context)


