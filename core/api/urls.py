from django.urls import path
from .views import GenerateMealPlanAPI

urlpatterns = [
    path('generate/', GenerateMealPlanAPI.as_view(), name='generate-plan'),
]