from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class AppUser(models.Model):
    WEIGHT_GOAL_CHOICES = [
        ("lose", "Lose Weight"),
        ("gain", "Gain Weight"),
        ("maintain", "Maintain Weight"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bmr = models.FloatField(blank=True, null=True)
    diseases = models.ManyToManyField("Disease", blank=True)
    dietary_restriction = models.CharField(max_length=255, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    gender = models.CharField(max_length=10, null=True, blank= True)
    age = models.IntegerField(null=True, blank=True)
    goal_weight = models.FloatField(blank=True, null=True)
    allergy = models.CharField(max_length=255, blank=True, null=True)
    meals_per = models.IntegerField(blank=True, null=True)
    snacks_per = models.IntegerField(blank=True, null=True)
    activity_level = models.CharField(max_length=50, blank=True, null=True)
    #Added additional fields for nutrition specific goals
    calorie_goal = models.FloatField(blank=True, null=True)
    carb_goal = models.FloatField(blank=True, null=True)
    protein_goal = models.FloatField(blank=True, null=True)
    fat_goal = models.FloatField(blank=True, null=True)
    weight_goal_type = models.CharField(
        max_length=20,
        choices=WEIGHT_GOAL_CHOICES,
        blank=True,
        null=True
    )



class Recipe(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    meal_type = models.CharField(max_length=255, blank=True, null=True)
	# measurement = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    serving = models.PositiveIntegerField(default=1)
	# substitutions = models.TextField(blank=True, null=True)
    how_to_cook = models.TextField(blank=True, null=True)

    def scale_ingredients(self, serving_size):
        """User puts desired serving size and it adjusts measurments to it"""
        try:
            return float(serving_size)/self.serving
        except (ValueError, ZeroDivisionError, TypeError):
            return 1.0
    
    def __str__(self):
        return f"{self.title} ({self.id})"

class Disease(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # add this
    related_diseases = models.TextField(blank=True, null=True)  # add this
    # superfood = models.CharField(max_length=255, blank=True, null=True)
    # must_avoid = models.TextField(blank=True, null=True)
    # recommended_activity_level = models.CharField(max_length=255, blank=True, null=True)


    # needs top and bottom range values:
    
    low_calories_kcal = models.FloatField(blank=True, null=True)
    high_calories_kcal = models.FloatField(blank=True, null=True)

    low_saturated_fat_g = models.FloatField(blank=True, null=True)
    high_saturated_fat_g = models.FloatField(blank=True, null=True)

    low_carbs_g = models.FloatField(blank=True, null=True)
    high_carbs_g = models.FloatField(blank=True, null=True)

    low_protein_g = models.FloatField(blank=True, null=True)
    high_protein_g = models.FloatField(blank=True, null=True)

    low_fiber_g = models.FloatField(blank=True, null=True)
    high_fiber_g = models.FloatField(blank=True, null=True)

    low_sugar_g = models.FloatField(blank=True, null=True)
    high_sugar_g = models.FloatField(blank=True, null=True)

    low_cholesterol_mg = models.FloatField(blank=True, null=True)
    high_cholesterol_mg = models.FloatField(blank=True, null=True)

    low_sodium_mg = models.FloatField(blank=True, null=True)
    high_sodium_mg = models.FloatField(blank=True, null=True)

    low_potassium_mg = models.FloatField(blank=True, null=True)
    high_potassium_mg = models.FloatField(blank=True, null=True)

    low_iron_mg = models.FloatField(blank=True, null=True)
    high_iron_mg = models.FloatField(blank=True, null=True)

    low_calcium_mg = models.FloatField(blank=True, null=True)
    high_calcium_mg = models.FloatField(blank=True, null=True)

    low_phosphorus_mg = models.FloatField(blank=True, null=True)
    high_phosphorus_mg = models.FloatField(blank=True, null=True)

    low_magnesium_mg = models.FloatField(blank=True, null=True)
    high_magnesium_mg = models.FloatField(blank=True, null=True)

    low_vitamin_a_ug = models.FloatField(blank=True, null=True)
    high_vitamin_a_ug = models.FloatField(blank=True, null=True)

    low_vitamin_b_mg = models.FloatField(blank=True, null=True)
    high_vitamin_b_mg = models.FloatField(blank=True, null=True)

    low_vitamin_c_mg = models.FloatField(blank=True, null=True)
    high_vitamin_c_mg = models.FloatField(blank=True, null=True)

    low_vitamin_d_ug = models.FloatField(blank=True, null=True)
    high_vitamin_d_ug = models.FloatField(blank=True, null=True)

    low_vitamin_e_mg = models.FloatField(blank=True, null=True)
    high_vitamin_e_mg = models.FloatField(blank=True, null=True)

    low_vitamin_k_ug = models.FloatField(blank=True, null=True)
    high_vitamin_k_ug = models.FloatField(blank=True, null=True)

    low_zinc_mg = models.FloatField(blank=True, null=True)
    high_zinc_mg = models.FloatField(blank=True, null=True)

    low_iodine_ug = models.FloatField(blank=True, null=True)
    high_iodine_ug = models.FloatField(blank=True, null=True)

    low_selenium_ug = models.FloatField(blank=True, null=True)
    high_selenium_ug = models.FloatField(blank=True, null=True)

    low_copper_mg = models.FloatField(blank=True, null=True)
    high_copper_mg = models.FloatField(blank=True, null=True)

    low_fluoride_mg = models.FloatField(blank=True, null=True)
    high_fluoride_mg = models.FloatField(blank=True, null=True)

    low_chromium_mg = models.FloatField(blank=True, null=True)
    high_chromium_mg = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.id})"
    

class Ingredient(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    measurements = models.TextField(blank=True, null=True)
    measurement_amount = models.FloatField(blank=True, null=True)

    calories_kcal = models.FloatField(blank=True, null=True)
    saturated_fat_g = models.FloatField(blank=True, null=True)
    carbs_g = models.FloatField(blank=True, null=True)
    protein_g = models.FloatField(blank=True, null=True)
    fiber_g = models.FloatField(blank=True, null=True)
    sugar_g = models.FloatField(blank=True, null=True)
    cholesterol_mg = models.FloatField(blank=True, null=True)
    sodium_mg = models.FloatField(blank=True, null=True)
    potassium_mg = models.FloatField(blank=True, null=True)
    iron_mg = models.FloatField(blank=True, null=True)
    calcium_mg = models.FloatField(blank=True, null=True)
    phosphorus_mg = models.FloatField(blank=True, null=True)
    magnesium_mg = models.FloatField(blank=True, null=True)

    vitamin_a_ug = models.FloatField(blank=True, null=True)
    vitamin_b_mg = models.FloatField(blank=True, null=True)
    vitamin_c_mg = models.FloatField(blank=True, null=True)
    vitamin_d_ug = models.FloatField(blank=True, null=True)
    vitamin_e_mg = models.FloatField(blank=True, null=True)
    vitamin_k_ug = models.FloatField(blank=True, null=True)

    zinc_mg = models.FloatField(blank=True, null=True)
    iodine_ug = models.FloatField(blank=True, null=True)
    selenium_ug = models.FloatField(blank=True, null=True)
    copper_mg = models.FloatField(blank=True, null=True)
    #magnesium_2_mg = models.FloatField(blank=True, null=True)
    fluoride_mg = models.FloatField(blank=True, null=True)
    chromium_mg = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.id})"


class Recipe_Ingredients(models.Model):
    recipe_id = models.ForeignKey(Recipe, null=True, on_delete=models.CASCADE)
    ingredient_id = models.ForeignKey(Ingredient, null=True, on_delete=models.CASCADE)
    amount=models.FloatField(blank=True,null=True)
    recipe_ingredient_id = models.AutoField(primary_key=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["recipe_id", "ingredient_id"], name="uniq_recipe_ingredient")
        ]


class Disease_Super_Food(models.Model):
    disease_id = models.ForeignKey(Disease, null=True, on_delete=models.CASCADE)
    ingredient_id = models.ForeignKey(Ingredient, null=True, on_delete=models.CASCADE)
    disease_ingredient_id = models.AutoField(primary_key=True)

    class Meta:
         constraints = [
              models.UniqueConstraint(fields=["disease_id", "ingredient_id"], name="uniq_disease_superfood")
         ]

class Disease_Avoid_Food(models.Model):
    disease_id = models.ForeignKey(Disease, null=True, on_delete=models.CASCADE)
    ingredient_id = models.ForeignKey(Ingredient, null=True, on_delete=models.CASCADE)
    disease_ingredient_id = models.AutoField(primary_key=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["disease_id", "ingredient_id"], name="uniq_disease_avoidfood")
        ]

class UserPickedRecipes(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    recipe = models.TextField(blank=True, null=True)  
    servings_requested = models.IntegerField(default=1)
    def __str__(self):
        recipe_preview = self.recipe[:50] if self.recipe else "No recipes"
        return f"{self.user.user.email} - {recipe_preview}"

    disease_ingredient_id = models.AutoField(primary_key=True)


class DailyLog(models.Model):
    """
    Stores daily nutrition intake for each user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField(default=timezone.now)
    
    # Daily totals
    total_calories = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fats = models.FloatField(default=0)
    total_burned = models.FloatField(default=0)
    calorie_goal = models.FloatField(default=2000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'date')  # One log per user per day
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"
    
    @property
    def net_calories(self):
        """Calories consumed minus calories burned"""
        return self.total_calories - self.total_burned
    
    @property
    def remaining_calories(self):
        """Calories remaining for the day"""
        return self.calorie_goal - self.net_calories


class MealEntry(models.Model):
    """
    Individual meals/food entries for a daily log
    """
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='meals')
    meal_name = models.CharField(max_length=200, default='Meal')
    calories = models.FloatField()
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)
    logged_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-logged_at']
    
    def __str__(self):
        return f"{self.meal_name} - {self.calories} kcal"


class WorkoutEntry(models.Model):
    """
    Workout/exercise entries for a daily log
    """
    WORKOUT_TYPES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('yoga', 'Yoga'),
        ('sports', 'Sports'),
        ('walking', 'Walking'),
        ('running', 'Running'),
        ('other', 'Other'),
    ]
    
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='workouts')
    workout_type = models.CharField(max_length=50, choices=WORKOUT_TYPES)
    calories_burned = models.FloatField()
    logged_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-logged_at']
    
    def __str__(self):
        return f"{self.workout_type} - {self.calories_burned} kcal burned"




class UserPickedDisease(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    disease = models.TextField(blank=True, null=True)  
    def __str__(self):
        disease_preview = self.disease[:50] if self.disease else "No disease"
        return f"{self.user.user.email} - {disease_preview}"

    disease_ingredient_id = models.AutoField(primary_key=True)


class Quote(models.Model):
     id = models.IntegerField(primary_key=True)
     quote = models.TextField()
     def __str__(self):
          return self.quote[:50]  # returns the first 50 characters of the quote for display purposes
     
class DietaryRestriction(models.Model):
     id=models.IntegerField(primary_key=True)
     title=models.CharField(max_length=255)

     def __str__(self):
            return self.title
     
class Dietary_Restriction_Ingredient(models.Model):
     dietary_restriction=models.ForeignKey(DietaryRestriction, null=True, on_delete=models.CASCADE)
     ingredient=models.ForeignKey(Ingredient, null=True, on_delete=models.CASCADE)

     def __str__(self):
          return f"{self.dietary_restriction.title} - {self.ingredient.title}"
     
class Dietary_Restriction_Recipe(models.Model):
        dietary_restriction=models.ForeignKey(DietaryRestriction, null=True, on_delete=models.CASCADE)
        recipe=models.ForeignKey(Recipe, null=True, on_delete=models.CASCADE)
    
        def __str__(self):
            return f"{self.dietary_restriction.title} - {self.recipe.title}"

class Goal(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_value = models.FloatField(blank=True, null=True)
    time_period = models.CharField(max_length=20, blank=True, null=True) # for weekly or daily
    completed = models.BooleanField(default=False)
    unit = models.CharField(max_length=50, blank=True, null=True) #calories, grams, etc.
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return f"{self.name} ({self.user.user.username})"
    
class WeightEntry(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="weight_entries")
    weight = models.FloatField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.user.username} - {self.weight}"