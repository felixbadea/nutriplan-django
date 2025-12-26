# core/admin.py
from django.contrib import admin
from .models import Restaurant, UserProfile, Dish, MacroRatio, MealPlan, Allergen, ClientMembership


# TITLURI FRUMOASE PENTRU ADMIN
admin.site.site_header = "NutriPlan Admin"
admin.site.site_title = "NutriPlan"
admin.site.index_title = "Panou administrare"


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__username']
    readonly_fields = ['slug', 'created_at']
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']

@admin.register(ClientMembership)
class ClientMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'role', 'joined_at']
    list_filter = ['role', 'restaurant', 'joined_at']
    search_fields = ['user__username', 'user__email', 'restaurant__name']
    raw_id_fields = ['user', 'restaurant']  # pentru performanță la mulți useri


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'meal_type', 'calories', 'is_default', 'is_active']
    list_filter = ['meal_type', 'restaurant', 'is_default', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active', 'is_default']
    list_per_page = 25
    list_display = ['name', 'restaurant', 'meal_type', 'calories', 'is_vegan', 'is_vegetarian', 'is_gluten_free', 'is_lactose_free', 'is_default', 'is_active']
    list_filter = ['meal_type', 'restaurant', 'is_vegan', 'is_vegetarian', 'is_gluten_free', 'is_lactose_free', 'is_default', 'is_active']
    filter_horizontal = ['allergens']  # Pentru ManyToMany

@admin.register(MacroRatio)
class MacroRatioAdmin(admin.ModelAdmin):
    list_display = ['name', 'proteins', 'carbs', 'fats', 'fiber_recommendation']
    list_editable = ['proteins', 'carbs', 'fats']


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_calories', 'macro_ratio', 'activity_level', 'created_at', 'bmi']
    list_filter = ['macro_ratio', 'activity_level', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'user_snapshot']
    date_hierarchy = 'created_at'
    list_per_page = 20

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ['name']