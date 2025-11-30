# core/management/commands/seed_macroratios.py
from django.core.management.base import BaseCommand
from core.models import MacroRatio

class Command(BaseCommand):
    help = 'Seed MacroRatio objects'

    def handle(self, *args, **options):
        ratios = [
            ("Echilibrat Standard", 30, 45, 25, "Raport clasic recomandat de majoritatea ghidurilor oficiale."),
            ("High-Protein (Slăbire)", 35, 35, 30, "Proteine ridicate pentru sațietate și păstrare masă musculară."),
            ("High-Protein Extrem", 40, 30, 30, "Ideal pentru definiție musculară și cutting agresiv."),
            ("Zona / 40-30-30", 40, 30, 30, "Raportul clasic din dieta Zone."),
            ("Low-Carb Moderată", 30, 25, 45, "Reducere moderată carbohidrați, intră în ardere grăsimi."),
            ("Ketogenică Standard", 20, 5, 75, "Cea mai populară variantă ketogenică."),
            ("Keto High-Protein (Gym)", 35, 5, 60, "Keto pentru cei care fac sală intens."),
            ("Carb Cycling / Anabolic", 35, 50, 15, "Zile de antrenament greu – carbohidrați mulți."),
            ("Creștere Masă (Bulking)", 25, 55, 20, "Bulking curat cu surplus caloric din carbohidrați."),
            ("Low-Fat (Old-School)", 25, 60, 15, "Stil clasic 90’s, încă folosit de alergători/maratonisti."),
        ]

        for name, p, c, f, desc in ratios:
            MacroRatio.objects.get_or_create(
                name=name,
                defaults={'proteins': p, 'carbs': c, 'fats': f, 'description': desc}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded MacroRatios!'))