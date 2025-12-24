# NutriPlan – Plan alimentar personalizat inteligent

Generare automată de plan alimentar pe 7 zile, cu:

- Calcule precise după greutate, înălțime, activitate și greutate țintă
- Macros personalizate (High Protein, Balanced, Low Carb etc.)
- Start dinamic: planul începe exact de la masa următoare (ex: ora 17:48 → începe cu Cina)
- Cantități exacte în grame pentru fiecare aliment
- Mesele trecute apar tăiate automat
- Interfață modernă cu HTMX + Bootstrap 5

### Demo live (în curând)

https://nutriplan.ro (coming soon)

### Tehnologii

- Django 5.1 + DRF
- PostgreSQL
- HTMX + Bootstrap 5
- Python 3.11+

### Cum rulezi local

```bash
git clone https://github.com/felixbadea/nutriplan-django.git
cd nutriplan-django
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata dishes
python manage.py runserver
```
