# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('generate-plan/', views.generate_plan_htmx, name='generate-plan'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('plan/<int:plan_id>/', views.plan_detail_view, name='view-plan'),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]