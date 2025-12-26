# core/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GenerateMealPlanSerializer, MealPlanResultSerializer 
from core.services import generate_meal_plan
from core.views import RestaurantRequiredMixin  # ← IMPORT IMPORTANT


class GenerateMealPlanAPI(RestaurantRequiredMixin, APIView):  # ← ADAUGĂ MIXIN-UL
    def post(self, request):
        serializer = GenerateMealPlanSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        plan_data = generate_meal_plan(
            serializer.validated_data,
            user=request.user if request.user.is_authenticated else None,
            restaurant=request.current_restaurant  # ← acum există garantat
        )

        result_serializer = MealPlanResultSerializer(plan_data)
        return Response(result_serializer.data, status=status.HTTP_200_OK)