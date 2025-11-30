# core/admin.py
from django.contrib import admin
from .models import Dish, MacroRatio, MealPlan


# TITLURI FRUMOASE PENTRU ADMIN
admin.site.site_header = "NutriPlan Admin"
admin.site.site_title = "NutriPlan"
admin.site.index_title = "Panou administrare"


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'calories', 'proteins', 'carbs', 'fats', 'is_active']
    list_filter = ['meal_type', 'is_active']
    search_fields = ['name']
    list_per_page = 25


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


