from django.contrib import admin
from django.urls import path
from recipes import views
from recipes import views as recipe_views

urlpatterns = [    
    path('admin/', admin.site.urls),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.registration_page, name='registration_page'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('recipes/', views.recipes_list, name='recipes_list'),
    path('recipes/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('add_to_picked_recipes/', views.add_to_picked_recipes, name='add_to_picked_recipes'),  
    path('selected_recipes/', views.selected_recipes, name='selected_recipes'),
    path('userprofile/', recipe_views.user_profile, name='user_profile'),
    path('forgot_pass/', views.forgot_password_page, name='forgot_pass'),
    # New endpoint for AJAX requests
    #path('', views.landing_page, name='landing_page'),
    path('diseases/', views.disease_page, name='disease_page'),
    path('diseases/<int:id>/', views.disease_detail, name='disease_detail'),
    path('grocery_list/', views.grocery_list, name='grocery_list'),
    path('daily/', views.daily_digest, name='daily_digest'),
    path('daily/', views.daily_digest, name='daily_digest'),
    path('api/daily/data/', views.get_daily_data, name='get_daily_data'),
    path('api/daily/add-meal/', views.add_meal, name='add_meal'),
    path('api/daily/add-workout/', views.add_workout, name='add_workout'),
    path('weekly_digest/', views.weekly_digest, name='weekly_digest'),
    path('selected_disease/', views.selected_disease, name='selected_disease'),
    path('add_to_picked_disease/', views.add_to_picked_disease, name='add_to_picked_disease'),
    path('custom_recipe/', views.custom_user_recipe, name='custom_recipe'),
    path('recipe_info/<int:recipe_id>', views.recipe_info, name='recipe_info'),
    path('remove_recipes/', views.remove_recipes, name='remove_recipes'),
    path("goals/", views.goals_page, name="goals_page"),
]
