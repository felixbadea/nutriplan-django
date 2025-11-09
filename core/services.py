import random
from .models import Dish


def calculate_bmr(profile):
    """Calculează BMR (Harris-Benedict)"""
    if profile.gender == 'M':
        return 10 * profile.weight + 6.25 * (profile.height or 170) - 5 * profile.age + 5
    else:
        return 10 * profile.weight + 6.25 * (profile.height or 160) - 5 * profile.age - 161


def calculate_tdee(profile):
    """Calculează TDEE în funcție de activitatea fizică"""
    multipliers = {
        'sedentar': 1.2,
        'usor': 1.375,
        'moderata': 1.55,
        'intensa': 1.725,
        'foarte_intensa': 1.9,
    }
    bmr = calculate_bmr(profile)
    return bmr * multipliers.get(profile.activity_level, 1.2)


def generate_meal_plan(profile, macro_ratio):
    """Generează planul alimentar complet"""
    tdee = calculate_tdee(profile)
    total_calories = round(tdee)

    # Macros în grame
    proteins_g = round((total_calories * macro_ratio.proteins / 100) / 4)
    carbs_g = round((total_calories * macro_ratio.carbs / 100) / 4)
    fats_g = round((total_calories * macro_ratio.fats / 100) / 9)

    # Împarte caloriile pe mese
    meal_split = {
        'mic_dejun': 0.25,
        'gustare1': 0.10,
        'pranz': 0.30,
        'gustare2': 0.10,
        'cina': 0.25,
    }

    meals = []
    for meal_type, percent in meal_split.items():
        target_cal = total_calories * percent
        dishes = select_dishes_for_meal(meal_type, target_cal)
        meals.append({
            'meal': meal_type.replace('_', ' ').title(),
            'dishes': dishes,
            'total_calories': sum(d['calories'] for d in dishes),
        })

    return {
        'daily_calories': total_calories,
        'macros': {
            'proteins': proteins_g,
            'carbs': carbs_g,
            'fats': fats_g,
            'fiber': macro_ratio.fiber_per_day,
        },
        'meals': meals,
    }


def select_dishes_for_meal(meal_type, target_calories):
    """Alege mâncăruri pentru o masă"""
    # Prioritate: mâncăruri specifice tipului de masă
    candidates = Dish.objects.filter(meal_type=meal_type)
    if not candidates.exists():
        candidates = Dish.objects.all()

    candidates = list(candidates.order_by('?')[:5])  # amestecă și ia 5
    if not candidates:
        return []

    selected = []
    remaining = target_calories

    for _ in range(3):  # max 3 feluri pe masă
        if remaining < 100 or not candidates:
            break

        dish = random.choice(candidates)
        max_portion = min(350, (remaining / dish.calories) * 100)
        portion = round(random.uniform(70, max_portion), -1)  # rotunjit la 10g
        if portion < 50:
            continue

        calories = round((dish.calories / 100) * portion)
        selected.append({
            'name': dish.name,
            'quantity': int(portion),
            'calories': calories,
        })
        remaining -= calories

    return selected