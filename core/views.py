
# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, FormView, ListView
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string

from .models import MealPlan, MacroRatio
from core.services import generate_meal_plan


# ==================== HOME + HTMX GENERARE PLAN ====================
class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['macro_ratios'] = MacroRatio.objects.all().order_by('name')
        return context


def generate_plan_htmx(request):
    if request.method != "POST":
        return HttpResponse('')

    try:
        # === Preluare și validare date ===
        age = int(request.POST['age'])
        gender = request.POST['gender']
        weight = float(request.POST['weight'])
        height = request.POST.get('height')
        height = float(height) if height else None
        target_weight = request.POST.get('target_weight')
        target_weight = float(target_weight) if target_weight else None
        activity_level = request.POST['activity_level']
        macro_ratio = MacroRatio.objects.get(id=request.POST['macro_ratio'])

        input_data = {
            'age': age,
            'gender': gender,
            'weight': weight,
            'height': height,
            'activity_level': activity_level,
            'macro_ratio': macro_ratio,
            'target_weight': target_weight,
        }

        # === Generare plan ===
        plan_data = generate_meal_plan(input_data, user=request.user if request.user.is_authenticated else None)

        # === SALVARE AUTOMATĂ dacă utilizatorul e logat ===
        if request.user.is_authenticated:
            bmi_value = round(weight / ((height / 100) ** 2), 1) if height else None
            
            MealPlan.objects.create(
                user=request.user,
                macro_ratio=macro_ratio,
                daily_calories=plan_data['daily_calories'],
                proteins=plan_data['macros']['proteins'],
                carbs=plan_data['macros']['carbs'],
                fats=plan_data['macros']['fats'],
                fiber=plan_data['macros']['fiber'],
                bmi=bmi_value,
                target_weight=target_weight,
                user_snapshot={
                    'age': age,
                    'gender': gender,
                    'weight': weight,
                    'height': height,
                    'activity_level': activity_level,
                }
            )

        # === Returnăm HTML-ul frumos ===
        html = render_to_string('core/partials/plan_result.html', {'plan': plan_data}, request=request)
        return HttpResponse(html)

    except Exception as e:
        return HttpResponse(f'''
            <div class="alert alert-danger text-center p-5 rounded-3 shadow">
                <h4>Eroare la generarea planului</h4>
                <p class="mb-0">{str(e)}</p>
            </div>
        ''', content_type='text/html')


# ==================== DASHBOARD ====================
class DashboardView(LoginRequiredMixin, ListView):
    model = MealPlan
    template_name = 'core/dashboard.html'
    context_object_name = 'plans'
    paginate_by = 10

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_plans'] = self.get_queryset().count()
        return context


# ==================== PLAN DETAIL ====================
@login_required
def plan_detail_view(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    
    # AICI ERA PROBLEMA: tu trimiteai doar macro-urile, dar template-ul așteaptă MESSELE!
    # Soluția: folosim user_snapshot (pe care îl salvăm în services.py)

    plan_data = plan.user_snapshot  # ← AICI e TOTUL: mesele, zilele, alimentele!

    return render(request, 'core/plan_detail.html', {
        'plan': plan,         # obiectul MealPlan (pentru daily_calories, created_at etc.)
        'plan_data': plan_data,  # tot planul cu mesele pe zile (exact ce ai generat la început)
    })


# ==================== AUTH ====================
class RegisterView(CreateView):
    template_name = 'core/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginView(FormView):
    template_name = 'core/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect(self.success_url)


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')