# core/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Eliminăm importul de render care nu mai e necesar
from .serializers import GenerateMealPlanSerializer, MealPlanResultSerializer 
from core.services import generate_meal_plan

class GenerateMealPlanAPI(APIView):
    def post(self, request):
        serializer = GenerateMealPlanSerializer(data=request.data)
        
        # Verificăm validitatea. Dacă NU este valid, OPRIM execuția aici și returnăm eroarea 400.
        if not serializer.is_valid():
            # DRF gestionează automat mesajele de eroare în format JSON aici
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # DACĂ ajungem la această linie, înseamnă că datele SUNT valide
        # și putem accesa safe `serializer.validated_data`.
        
        # Apelăm logica de serviciu care returnează un dicționar Python (plan_data)
        plan_data = generate_meal_plan(
            serializer.validated_data, # Folosim datele validate
            user=request.user if request.user.is_authenticated else None
        )

        # Folosim noul serializator pentru a formata dicționarul plan_data în JSON
        result_serializer = MealPlanResultSerializer(plan_data)
        
        # Returnează răspunsul JSON cu status 200 OK
        return Response(result_serializer.data, status=status.HTTP_200_OK)