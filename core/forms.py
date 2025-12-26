# core\forms.py
from django import forms
from .models import MacroRatio, Allergen  # ← Adaugă Allergen


class MealPlanForm(forms.Form):
    age = forms.IntegerField(
        min_value=18, max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'ex: 30',
            'min': '18',
            'max': '100'
        })
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Bărbat'), ('F', 'Femeie')],
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )
    weight = forms.FloatField(
        min_value=30, max_value=200,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'step': '0.1',
            'placeholder': 'ex: 75.5'
        })
    )
    height = forms.FloatField(
        min_value=100, max_value=250, required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'ex: 175'
        })
    )
    activity_level = forms.ChoiceField(
        choices=[
            ('sedentary', 'Sedentar'),
            ('light', 'Activitate ușoară'),
            ('moderate', 'Activitate moderată'),
            ('active', 'Activitate intensă'),
            ('very_active', 'Foarte intensă'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )
    macro_ratio = forms.ModelChoiceField(
        queryset=MacroRatio.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )
    target_weight = forms.FloatField(
        min_value=40, max_value=150, required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'ex: 70 (opțional)',
            'step': '0.1'
        })
    )

    # ==================== NOI CÂMPURI DIETETICE ====================
    is_vegan = forms.BooleanField(required=False, initial=False)
    is_vegetarian = forms.BooleanField(required=False, initial=False)
    is_raw_vegan = forms.BooleanField(required=False, initial=False)
    is_gluten_free = forms.BooleanField(required=False, initial=False)
    is_lactose_free = forms.BooleanField(required=False, initial=False)
    allergens = forms.ModelMultipleChoiceField(
        queryset=Allergen.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select form-select-lg'})
    )
       
    
   