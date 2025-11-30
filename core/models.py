# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator   # AICI ERA PROBLEMA!


GENDER_CHOICES = [('M', 'Masculin'), ('F', 'Feminin')]

ACTIVITY_LEVELS = [
    ('sedentary', 'Sedentar'),
    ('light', 'Activitate ușoară'),
    ('moderate', 'Activitate moderată'),
    ('active', 'Activitate intensă'),
    ('very_active', 'Foarte intensă'),
]

MEAL_TYPES = [
    ('mic_dejun', 'Mic dejun'),
    ('gustare1', 'Gustare 1'),
    ('pranz', 'Prânz'),
    ('gustare2', 'Gustare 2'),
    ('cina', 'Cinǎ'),
]


#

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class MacroRatio(models.Model):
    name = models.CharField(max_length=60, unique=True)
    proteins = models.PositiveSmallIntegerField()
    carbs = models.PositiveSmallIntegerField()
    fats = models.PositiveSmallIntegerField()
    fiber_recommendation = models.CharField(max_length=50, default="14g / 1000 kcal")
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.name} ({self.proteins}-{self.carbs}-{self.fats})"


class Dish(models.Model):
    name = models.CharField(max_length=120)
    calories = models.FloatField(help_text="kcal / 100g")
    proteins = models.FloatField(help_text="g / 100g")
    carbs = models.FloatField(help_text="g / 100g")
    fats = models.FloatField(help_text="g / 100g")
    fiber = models.FloatField(default=0)
    portion_size = models.FloatField(default=100)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} – {self.calories} kcal/100g"


class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    macro_ratio = models.ForeignKey(MacroRatio, on_delete=models.PROTECT)

    daily_calories = models.PositiveIntegerField()
    proteins = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField()
    fats = models.PositiveIntegerField()
    fiber = models.PositiveIntegerField()

    bmi = models.FloatField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS, default='moderate')

    # ADAUGĂ ACESTE LINII – SOLUȚIA TA!
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)

    user_snapshot = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Plan {self.user.username} – {self.daily_calories} kcal"
