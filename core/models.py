# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


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


# ==================== RESTAURANT ====================
class Restaurant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_restaurants')
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='restaurants/logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Restaurant.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)


# ==================== USER PROFILE ====================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Proprietar'),
            ('admin', 'Administrator'),
            ('staff', 'Personal'),
        ],
        default='staff'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # ← ADAUGĂ null=True, blank=True

    def __str__(self):
        return f"{self.user.username} ({self.role} @ {self.restaurant.name})"

    class Meta:
        unique_together = ('user', 'restaurant')


# ==================== MACRO RATIO ====================
class MacroRatio(models.Model):
    name = models.CharField(max_length=60, unique=True)
    proteins = models.PositiveSmallIntegerField()
    carbs = models.PositiveSmallIntegerField()
    fats = models.PositiveSmallIntegerField()
    fiber_recommendation = models.CharField(max_length=50, default="14g / 1000 kcal")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (P:{self.proteins}% C:{self.carbs}% G:{self.fats}%)"


# ==================== DISH ====================
class Dish(models.Model):
    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    calories = models.PositiveIntegerField(help_text="kcal per 100g")
    proteins = models.DecimalField(max_digits=5, decimal_places=1, help_text="g per 100g")
    carbs = models.DecimalField(max_digits=5, decimal_places=1, help_text="g per 100g")
    fats = models.DecimalField(max_digits=5, decimal_places=1, help_text="g per 100g")
    fiber = models.DecimalField(
        max_digits=5, 
        decimal_places=1, 
        default=0.0,
        help_text="g fibre per 100g"
    )
    image = models.ImageField(upload_to='dishes/', null=True, blank=True)


    # MULTI-RESTAURANT
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')
    is_default = models.BooleanField(
        default=False,
        help_text="Dacă este bifat, acest aliment este disponibil pentru TOATE restaurantele"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} – {self.calories} kcal/100g"

    class Meta:
        unique_together = ('name', 'restaurant')
        ordering = ['name']


# ==================== MEAL PLAN ====================
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


# ==================== SIGNAL PENTRU USER PROFILE ====================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creează automat UserProfile la înregistrarea unui user nou.
    Restaurantul este asignat temporar prin atributul _restaurant_to_assign în view.
    """
    if created and hasattr(instance, '_restaurant_to_assign'):
        restaurant = instance._restaurant_to_assign
        UserProfile.objects.create(
            user=instance,
            restaurant=restaurant,
            role='staff'  # clienții obișnuiți sunt staff (sau poți schimba în 'client' dacă vrei)
        )
        del instance._restaurant_to_assign