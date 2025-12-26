# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)  # ex: "Nuci", "Ouă", "Lapte"
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
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
    clients = models.ManyToManyField(
        User,
        through='ClientMembership',
        related_name='restaurants_joined',
        blank=True
    )

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
    # Preferințe globale (opțional, ex: unitate de măsură, limbă etc.)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class ClientMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=20,
        choices=[('client', 'Client'), ('favorite', 'Preferat')],
        default='client'
    )
    # Poți adăuga câmpuri suplimentare per restaurant: preferințe specifice, puncte loialitate etc.

    class Meta:
        unique_together = ('user', 'restaurant')  # un user nu poate fi de 2 ori client la același restaurant


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
    is_vegan = models.BooleanField(default=False, help_text="Fără produse animale")
    is_vegetarian = models.BooleanField(default=False, help_text="Fără carne, dar poate lactate/ouă")
    is_raw_vegan = models.BooleanField(default=False, help_text="Raw și vegan")
    is_gluten_free = models.BooleanField(default=False)
    is_lactose_free = models.BooleanField(default=False)
    allergens = models.ManyToManyField(Allergen, blank=True, related_name='dishes')
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
    dietary_constraints = models.JSONField(default=dict, blank=True)  # ex: {'vegan': True, 'gluten_free': True, 'allergens': [1,2]}
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
def add_user_to_restaurant(sender, instance, created, **kwargs):
    if created and hasattr(instance, '_restaurant_to_assign'):
        restaurant = instance._restaurant_to_assign
        # Creează asocierea client-restaurant
        ClientMembership.objects.create(
            user=instance,
            restaurant=restaurant,
            role='client'  # sau 'staff' dacă e owner
        )
        del instance._restaurant_to_assign

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    meal_plan = models.ForeignKey(MealPlan, null=True, on_delete=models.SET_NULL)
    dishes = models.ManyToManyField(Dish, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'În așteptare'), ('paid', 'Plătit'), ('delivered', 'Livrat')])
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)