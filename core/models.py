from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = [('M', 'Masculin'), ('F', 'Feminin')]
    ACTIVITY_LEVELS = [
        ('sedentar', 'Sedentar'),
        ('usor', 'Activitate ușoară'),
        ('moderata', 'Activitate moderată'),
        ('intensa', 'Activitate intensă'),
        ('foarte_intensa', 'Foarte intensă'),
    ]

    age = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    weight = models.FloatField(help_text="kg")
    height = models.FloatField(help_text="cm", null=True, blank=True)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS)

    def __str__(self):
        return f"{self.age} ani, {self.get_gender_display()}, {self.weight}kg"


class MacroRatio(models.Model):
    name = models.CharField(max_length=50, unique=True)
    proteins = models.FloatField(help_text="Procentaj proteine (%)")
    carbs = models.FloatField(help_text="Procentaj carbohidrați (%)")
    fats = models.FloatField(help_text="Procentaj grăsimi (%)")
    fiber_per_day = models.FloatField(default=30, help_text="Fibre recomandate (g/zi)")
    description = models.CharField(max_length=200, blank=True, help_text="Explicație pentru utilizator")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Raport Nutrițional"
        verbose_name_plural = "Rapoarte Nutriționale"


class Dish(models.Model):
    MEAL_TYPES = [
        ('mic_dejun', 'Mic dejun'),
        ('gustare1', 'Gustare 1'),
        ('pranz', 'Prânz'),
        ('gustare2', 'Gustare 2'),
        ('cina', 'Cinǎ'),
    ]

    name = models.CharField(max_length=100)
    calories = models.FloatField(help_text="kcal / 100g")
    proteins = models.FloatField(help_text="g / 100g")
    carbs = models.FloatField(help_text="g / 100g")
    fats = models.FloatField(help_text="g / 100g")
    fiber = models.FloatField(default=0, help_text="g / 100g")
    portion_size = models.FloatField(default=100, help_text="g")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.calories} kcal/100g)"
    
class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=[('M', 'Bărbat'), ('F', 'Femeie')])
    weight = models.FloatField()
    height = models.FloatField(null=True, blank=True)
    
    ACTIVITY_CHOICES = [
        ('sedentar', 'Sedentar'),
        ('usor', 'Ușoară'),
        ('moderata', 'Moderată'),
        ('intensa', 'Intensă'),
        ('foarte_intensa', 'Foarte intensă'),
    ]
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    
    macro_ratio = models.ForeignKey(MacroRatio, on_delete=models.PROTECT)
    daily_calories = models.PositiveIntegerField()
    proteins = models.PositiveIntegerField()
    carbs = models.PositiveIntegerField()
    fats = models.PositiveIntegerField()
    fiber = models.PositiveIntegerField()
    bmi = models.FloatField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True, help_text="Greutate țintă (kg)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan {self.user.username} - {self.daily_calories} kcal"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Plan Alimentar"
        verbose_name_plural = "Planuri Alimentare"
# Create your models here.
