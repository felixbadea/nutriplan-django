from django import forms
from .models import MacroRatio

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
            ('sedentar', 'Sedentar'),
            ('usor', 'Ușoară'),
            ('moderata', 'Moderată'),
            ('intensa', 'Intensă'),
            ('foarte_intensa', 'Foarte intensă'),
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

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get('weight')
        height = cleaned_data.get('height')

        if weight and height:
            bmi = weight / ((height / 100) ** 2)
            cleaned_data['bmi'] = round(bmi, 1)
            self.bmi = bmi  # pentru view
        return cleaned_data
       
    
   