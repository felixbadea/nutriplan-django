
# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, FormView, ListView
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string

from .models import MealPlan, MacroRatio, Restaurant
from .forms import MealPlanForm
from core.services import generate_meal_plan


# ==================== MIXIN PENTRU RESTAURANT ====================
class RestaurantRequiredMixin:
    """
    Mixin care validează slug-ul restaurantului și îl atașează la request.
    """
    def dispatch(self, request, *args, **kwargs):
        restaurant_slug = kwargs.get('restaurant_slug')
        if not restaurant_slug:
            return HttpResponseNotFound("Restaurant negăsit.")

        try:
            restaurant = Restaurant.objects.get(slug=restaurant_slug, is_active=True)
        except Restaurant.DoesNotExist:
            return HttpResponseNotFound("Restaurantul nu există sau nu este activ.")

        request.current_restaurant = restaurant
        return super().dispatch(request, *args, **kwargs)


# ==================== HOME VIEW ====================
class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['macro_ratios'] = MacroRatio.objects.all().order_by('name')
        context['form'] = MealPlanForm()

        restaurant_slug = self.kwargs.get('restaurant_slug')
        if restaurant_slug:
            try:
                restaurant = Restaurant.objects.get(slug=restaurant_slug, is_active=True)
                context['restaurant'] = restaurant
                self.request.current_restaurant = restaurant
            except Restaurant.DoesNotExist:
                context['restaurant'] = None
        else:
            context['restaurants'] = Restaurant.objects.filter(is_active=True).order_by('name')

        return context


# ==================== GENERARE PLAN HTMX ====================
def generate_plan_htmx(request):
    if request.method != "POST":
        return HttpResponse('')

    restaurant = getattr(request, 'current_restaurant', None)
    if not restaurant:
        return HttpResponse("Restaurant negăsit.", status=400)

    form = MealPlanForm(request.POST)
    if not form.is_valid():
        html = render_to_string('core/partials/form_errors.html', {'form': form}, request=request)
        return HttpResponse(html)

    cleaned_data = form.cleaned_data
    cleaned_data['macro_ratio'] = form.cleaned_data['macro_ratio']

    plan_data = generate_meal_plan(
        data=cleaned_data,
        user=request.user if request.user.is_authenticated else None,
        restaurant=restaurant
    )

    if request.user.is_authenticated:
        template = 'core/partials/plan_saved.html'
    else:
        template = 'core/partials/plan_generated.html'

    html = render_to_string(template, {
        'plan_data': plan_data,
        'restaurant': restaurant,
        'user': request.user
    }, request=request)

    return HttpResponse(html)


# ==================== DASHBOARD ====================
class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'core/dashboard.html'
    context_object_name = 'plans'
    paginate_by = 12

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_plans'] = self.get_queryset().count()

        if hasattr(self.request, 'current_restaurant'):
            context['restaurant'] = self.request.current_restaurant

        return context


# ==================== PLAN DETAIL ====================
@login_required
def plan_detail_view(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    plan_data = plan.user_snapshot

    restaurant = getattr(request, 'current_restaurant', None)

    return render(request, 'core/plan_detail.html', {
        'plan': plan,
        'plan_data': plan_data,
        'restaurant': restaurant,
    })


# ==================== AUTH ====================
class RegisterView(CreateView):
    template_name = 'core/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        restaurant = getattr(request, 'current_restaurant', None)
        if not restaurant:
            return HttpResponseNotFound("Restaurant negăsit.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Atribuim temporar restaurantul pentru signal
        form.instance._restaurant_to_assign = self.request.current_restaurant
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = getattr(self.request, 'current_restaurant', None)
        return context


class LoginView(FormView):
    template_name = 'core/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = getattr(self.request, 'current_restaurant', None)
        return context

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect(self.success_url)


@login_required
def logout_view(request):
    logout(request)
    restaurant = getattr(request, 'current_restaurant', None)
    if restaurant:
        return redirect('/')
    return redirect('home')