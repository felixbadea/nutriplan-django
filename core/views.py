# Create your views here.

from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import MealPlanForm
from .services import generate_meal_plan
from .models import MealPlan, MacroRatio

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy

class RegisterView(CreateView):
    template_name = 'core/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Loghează automat după înregistrare
        return response

def get_recommended_ratio(bmi, age):
    """Alege raportul optim în funcție de BMI și vârstă"""
    try:
        if bmi < 18.5:
            return MacroRatio.objects.get(name__icontains="Creștere")
        elif 18.5 <= bmi <= 24.9:
            base = MacroRatio.objects.get(name__icontains="Menținere")
        elif 25 <= bmi <= 29.9:
            base = MacroRatio.objects.get(name__icontains="Slăbire")
        else:
            base = MacroRatio.objects.get(name__icontains="Rapidă")

        # Ajustare pentru vârstă
        if age > 50:
            high_protein = MacroRatio.objects.filter(proteins__gte=30).first()
            return high_protein or base
        return base
    except MacroRatio.DoesNotExist:
        return MacroRatio.objects.first()

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['macro_ratios'] = MacroRatio.objects.all()
        return context

class GeneratePlanView(LoginRequiredMixin, FormView):
    template_name = 'core/generate.html'
    form_class = MealPlanForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        profile_data = form.cleaned_data
        profile = type('Profile', (), profile_data)()
        bmi = getattr(form, 'bmi', None)

        # Alege raportul
        recommended_ratio = get_recommended_ratio(bmi, profile.age) if bmi else None
        selected_ratio = profile_data['macro_ratio']

        # Generează planul
        plan_data = generate_meal_plan(profile, selected_ratio)

        # Ajustare calorii pentru BMI
        if bmi and bmi > 25:
            plan_data['daily_calories'] = int(plan_data['daily_calories'] * 0.85)
        elif bmi and bmi < 18.5:
            plan_data['daily_calories'] = int(plan_data['daily_calories'] * 1.15)

        # SALVEAZĂ target_weight
        target_weight = profile_data.get('target_weight')

        # Salvează în DB
        MealPlan.objects.create(
            user=self.request.user,
            age=profile.age,
            gender=profile.gender,
            weight=profile.weight,
            height=profile.height,
            activity_level=profile.activity_level,
            macro_ratio=selected_ratio,
            daily_calories=plan_data['daily_calories'],
            proteins=plan_data['macros']['proteins'],
            carbs=plan_data['macros']['carbs'],
            fats=plan_data['macros']['fats'],
            fiber=plan_data['macros']['fiber'],
            bmi=round(bmi, 1) if bmi else None,
            target_weight=target_weight,  # AICI SE SALVEAZĂ
        )

        # Salvează în sesiune
        self.request.session['last_plan'] = plan_data
        self.request.session['bmi'] = round(bmi, 1) if bmi else None
        self.request.session['recommended_ratio'] = recommended_ratio.name if recommended_ratio else None

        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, ListView):
    model = MealPlan
    template_name = 'core/dashboard.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_plan = self.get_queryset().first()

        if latest_plan:
            bmi = latest_plan.bmi
            current_weight = latest_plan.weight
            target_weight = latest_plan.target_weight

            # === BMI STATUS ===
            if bmi < 18.5:
                context['bmi_status'] = 'Subponderal'
                context['bmi_class'] = 'bg-warning'
            elif bmi <= 24.9:
                context['bmi_status'] = 'Normal'
                context['bmi_class'] = 'bg-success'
            elif bmi <= 29.9:
                context['bmi_status'] = 'Supraponderal'
                context['bmi_class'] = 'bg-warning'
            else:
                context['bmi_status'] = 'Obezitate'
                context['bmi_class'] = 'bg-danger'
            context['latest_bmi'] = bmi

            # === PROGRES GREUTATE ===
            if target_weight and current_weight:
                diff = abs(current_weight - target_weight)
                weeks = diff / 0.5
                days = int(weeks * 7)

                # PROGRES CORECT: față de distanța inițială
                initial_diff = diff  # la acest plan (poți salva greutatea inițială în viitor)
                if initial_diff == 0:
                    progress = 100.0
                else:
                    progress = round((1 - diff / initial_diff) * 100, 1)
                    progress = max(0, min(100, progress))  # între 0% și 100%

                # Determinăm dacă e creștere sau scădere
                is_gaining = current_weight < target_weight

                context.update({
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'weight_diff': round(diff, 1),
                    'days_to_goal': days,
                    'progress_percent': progress,
                    'is_gaining': is_gaining,
                })

        return context
    

    

