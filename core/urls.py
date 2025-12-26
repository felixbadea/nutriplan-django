# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Aceste rute vor fi accesate ca /nume-restaurant/login/ , /nume-restaurant/register/ etc.
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Opțional: dacă vrei un dashboard specific restaurantului (ex. /alimente-default/dashboard/)
    path('dashboard/', views.DashboardView.as_view(), name='restaurant_dashboard'),

    # Alte rute specifice restaurantului
    path('generate-plan/', views.generate_plan_htmx, name='generate-plan'),
    path('plan/<int:plan_id>/', views.plan_detail_view, name='view-plan'),

    # Dacă mai ai alte rute specifice (ex. alimente, meniu etc.), le pui aici
    # path('alimente/', views.AlimenteView.as_view(), name='alimente'),
]