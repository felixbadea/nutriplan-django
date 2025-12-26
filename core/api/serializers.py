# core/api/serializers.py
from rest_framework import serializers
from core.models import MacroRatio, Allergen


class GenerateMealPlanSerializer(serializers.Serializer):
    gender = serializers.ChoiceField(choices=[('M', 'Masculin'), ('F', 'Feminin')])
    age = serializers.IntegerField(min_value=15, max_value=100)
    weight = serializers.FloatField(min_value=30, max_value=300)
    height = serializers.FloatField(min_value=100, max_value=250, required=False, allow_null=True)
    activity_level = serializers.ChoiceField(choices=[
        ('sedentary', 'Sedentar'),
        ('light', 'Activitate ușoară'),
        ('moderate', 'Activitate moderată'),
        ('active', 'Activitate intensă'),
        ('very_active', 'Foarte intensă'),
    ])
    macro_ratio = serializers.PrimaryKeyRelatedField(
        queryset=MacroRatio.objects.all()
    )

    # Restricții dietetice
    is_vegan = serializers.BooleanField(default=False, required=False)
    is_vegetarian = serializers.BooleanField(default=False, required=False)
    is_raw_vegan = serializers.BooleanField(default=False, required=False)
    is_gluten_free = serializers.BooleanField(default=False, required=False)
    is_lactose_free = serializers.BooleanField(default=False, required=False)
    allergens = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Allergen.objects.all(),
        required=False
    )


class MealPlanResultSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(max_length=200)
    daily_calories = serializers.IntegerField()
    bmi = serializers.FloatField(allow_null=True)
    proteins = serializers.IntegerField()
    carbs = serializers.IntegerField()
    fats = serializers.IntegerField()
    fiber = serializers.IntegerField()
    saved_plan_id = serializers.IntegerField(allow_null=True, required=False)
    meals = serializers.JSONField() 