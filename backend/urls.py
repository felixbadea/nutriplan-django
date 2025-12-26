# backend/urls.py
"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importăm view-ul pentru landing page (lista restaurante)
from core.views import RestaurantListView  # schimbat la RestaurantListView
from core.views import logout_view, DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.api.urls')),

    # Pagina principală – lista tuturor restaurantelor
    path('', RestaurantListView.as_view(), name='landing_home'),

    # Dashboard global (dacă vrei unul separat de cel per restaurant)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Logout global
    path('logout/', logout_view, name='logout'),

    # Toate rutele specifice unui restaurant (login, register, alimente, dashboard etc.)
    path('<slug:restaurant_slug>/', include('core.urls')),
]

# Servește fișiere statice și media în development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)