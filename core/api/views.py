from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import UserProfile, MacroRatio
from ..services import generate_meal_plan

class GenerateMealPlanAPI(APIView):
    def post(self, request):
        try:
            # Construim profilul temporar
            profile = UserProfile(
                age=int(request.data['age']),
                gender=request.data['gender'],
                weight=float(request.data['weight']),
                height=float(request.data.get('height', 170) or 170),
                activity_level=request.data['activity_level'],
            )
            macro_ratio = MacroRatio.objects.get(id=request.data['macro_ratio'])
            plan = generate_meal_plan(profile, macro_ratio)
            return Response(plan)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)