import random
from datetime import datetime, timedelta
from django.db import models
from core.models import Dish, MacroRatio, MealPlan, Restaurant


# ==================== CONFIGURAȚII ====================
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}

MEAL_CALORIE_DISTRIBUTION = {
    'mic_dejun': 0.25,
    'gustare1': 0.10,
    'pranz': 0.30,
    'gustare2': 0.10,
    'cina': 0.25,
}

MEAL_ORDER_DISPLAY = [
    "Mic Dejun",
    "Gustare 1",
    "Prânz",
    "Gustare 2",
    "Cină"
]

MEAL_TYPE_MAPPING = {
    "Mic Dejun": "mic_dejun",
    "Gustare 1": "gustare1",
    "Prânz": "pranz",
    "Gustare 2": "gustare2",
    "Cină": "cina",
}

ROMANIAN_DAYS = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]


# ==================== ORA CURENTĂ → MASA DE START ====================
def get_meal_start_info():
    now = datetime.now()
    current_time = now.hour + now.minute / 60.0

    if current_time < 9.5:          # până la 09:30
        return "Mic Dejun", 0, "Azi"
    elif current_time < 11.0:       # până la 11:00
        return "Gustare 1", 0, "Azi"
    elif current_time < 13.5:       # până la 13:30
        return "Prânz", 0, "Azi"
    elif current_time < 17.0:       # până la 17:00
        return "Gustare 2", 0, "Azi"
    elif current_time < 20.5:       # până la 20:30 → Cină
        return "Cină", 0, "Azi"
    else:                           # după 20:30 → începe mâine
        return "Mic Dejun", 1, "Mâine"


# ==================== ZILELE SĂPTĂMÂNII ====================
def get_week_days_labels(days_offset, first_day_label):
    base_date = datetime.now().date() + timedelta(days=days_offset)
    labels = []
    for i in range(7):
        day_date = base_date + timedelta(days=i)
        weekday_name = ROMANIAN_DAYS[day_date.weekday()]

        if i == 0:
            labels.append(first_day_label)
        elif i == 1 and days_offset == 1:
            labels.append("Azi")
        else:
            labels.append(weekday_name)
    return labels


# ==================== CALCUL CALORII + GREUTATE ȚINTĂ ====================
def calculate_daily_calories(data):
    gender = data['gender']
    age = int(data['age'])
    weight = float(data['weight'])
    height = float(data.get('height') or 170)
    target_weight = data.get('target_weight')
    activity_level = data['activity_level']

    # Mifflin-St Jeor
    if gender == 'M':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)

    if target_weight:
        target_weight = float(target_weight)
        diff = target_weight - weight
        if abs(diff) > 0.5:
            adj = 550 if diff > 0 else -550
            tdee += adj
        elif abs(diff) > 0.1:
            adj = 300 if diff > 0 else -300
            tdee += adj

    daily_calories = max(round(tdee / 50) * 50, 1200)
    return int(daily_calories)


# ==================== RESTUL FUNCȚIILOR ====================
def calculate_bmi(weight, height):
    if not height or height <= 0:
        return None
    return round(weight / ((height / 100) ** 2), 1)


def calculate_macros(daily_calories, macro_ratio):
    proteins = int((daily_calories * macro_ratio.proteins / 100) / 4)
    carbs = int((daily_calories * macro_ratio.carbs / 100) / 4)
    fats = int((daily_calories * macro_ratio.fats / 100) / 9)
    fiber = max(25, min(38, carbs // 12))
    return proteins, carbs, fats, fiber


def get_dishes_for_meal(meal_type_db, restaurant):
    """
    Returnează maxim 12 feluri active pentru tipul de masă,
    doar din restaurantul curent sau cele default (globale).
    """
    return list(
        Dish.objects.filter(
            models.Q(restaurant=restaurant) | models.Q(is_default=True),
            is_active=True,
            meal_type=meal_type_db
        )
        .order_by('?')[:12]
    )


def select_and_scale_dishes(meal_type_db, target_calories, target_p, target_c, target_f, restaurant):
    candidates = get_dishes_for_meal(meal_type_db, restaurant)
    if not candidates:
        return [{
            "name": "Opțiune manuală recomandată",
            "grams": 0,
            "calories": 0,
            "proteins": 0,
            "carbs": 0,
            "fats": 0,
            "is_past": False
        }]

    selected = []
    remaining_cal = target_calories
    num_dishes = random.choice([1, 2, 2, 3])

    for dish in candidates[:num_dishes]:
        if remaining_cal < 120:
            break
        grams = random.randint(80, 380)
        grams = min(grams, int(remaining_cal / (dish.calories / 100 * 0.8)))
        grams = round(grams / 10) * 10

        selected.append({
            "name": dish.name,
            "grams": int(grams),
            "calories": round((dish.calories / 100) * grams),
            "proteins": round((dish.proteins / 100) * grams),
            "carbs": round((dish.carbs / 100) * grams),
            "fats": round((dish.fats / 100) * grams),
            "is_past": False
        })
        remaining_cal -= selected[-1]["calories"]

    return selected


# ==================== GENERARE PLAN COMPLET ====================
def generate_weekly_meals(daily_calories, total_proteins, total_carbs, total_fats, restaurant):
    plan = {}
    start_meal_name, days_offset, first_day_label = get_meal_start_info()
    week_days = get_week_days_labels(days_offset, first_day_label)
    start_index = MEAL_ORDER_DISPLAY.index(start_meal_name)

    for day_idx, day_name in enumerate(week_days):
        day_meals = {}
        meals_to_show = MEAL_ORDER_DISPLAY[start_index:] if day_idx == 0 else MEAL_ORDER_DISPLAY

        # Mesele din trecut (doar în prima zi)
        if day_idx == 0 and start_index > 0:
            for past_meal in MEAL_ORDER_DISPLAY[:start_index]:
                day_meals[past_meal] = [{
                    "name": f"→ {past_meal} deja trecut",
                    "grams": 0,
                    "calories": 0,
                    "proteins": 0,
                    "carbs": 0,
                    "fats": 0,
                    "is_past": True
                }]

        # Mesele active
        for display_name in meals_to_show:
            meal_type_db = MEAL_TYPE_MAPPING[display_name]
            cal_pct = MEAL_CALORIE_DISTRIBUTION[meal_type_db]
            meal_cal = int(daily_calories * cal_pct + 5)
            meal_p = int(total_proteins * cal_pct)
            meal_c = int(total_carbs * cal_pct)
            meal_f = int(total_fats * cal_pct)

            dishes = select_and_scale_dishes(meal_type_db, meal_cal, meal_p, meal_c, meal_f, restaurant)
            day_meals[display_name] = dishes

        plan[day_name] = day_meals
        start_index = 0  # doar prima zi începe mai târziu

    return plan


# ==================== FUNCȚIA PRINCIPALĂ (AJUSTATĂ PENTRU MULTI-RESTAURANT) ====================
def generate_meal_plan(data, user=None, restaurant=None):
    """
    Generează planul alimentar personalizat.
    
    Args:
        data (dict): Datele din formular (age, gender, weight etc.)
        user (User, optional): Utilizatorul autentificat
        restaurant (Restaurant): Restaurantul curent – OBLIGATORIU pentru multi-tenant
    
    Returns:
        dict: Planul generat + metadate
    """
    if restaurant is None:
        raise ValueError("Restaurantul este obligatoriu pentru generarea planului.")

    daily_calories = calculate_daily_calories(data)
    bmi = calculate_bmi(data['weight'], data.get('height'))
    macro_ratio = data['macro_ratio']

    proteins, carbs, fats, fiber = calculate_macros(daily_calories, macro_ratio)
    meals = generate_weekly_meals(daily_calories, proteins, carbs, fats, restaurant)

    saved_plan = None
    if user and user.is_authenticated:
        saved_plan = MealPlan.objects.create(
            user=user,
            macro_ratio=macro_ratio,
            daily_calories=daily_calories,
            proteins=proteins,
            carbs=carbs,
            fats=fats,
            fiber=fiber,
            bmi=bmi,
            target_weight=data.get('target_weight'),
            activity_level=data['activity_level'],
            age=data['age'],
            gender=data['gender'],
            weight=data['weight'],
            height=data.get('height'),
            user_snapshot={
                "daily_calories": daily_calories,
                "bmi": bmi,
                "proteins": proteins,
                "carbs": carbs,
                "fats": fats,
                "fiber": fiber,
                "meals": meals,
                "generated_at": datetime.now().isoformat(),
                "restaurant_id": restaurant.id,
                "restaurant_name": restaurant.name,
            }
        )

    return {
        "success": True,
        "message": "Planul tău personalizat a fost generat cu succes!",
        "daily_calories": daily_calories,
        "bmi": bmi,
        "proteins": proteins,
        "carbs": carbs,
        "fats": fats,
        "fiber": fiber,
        "meals": meals,
        "saved_plan_id": saved_plan.id if saved_plan else None,
    }