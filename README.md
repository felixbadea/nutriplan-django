# NutriPlan - Plan Alimentar Personalizat

Aplicație Django cu:

- Calcul BMI
- Greutate țintă + progres
- Grafic evoluție
- Notificări email la 90%
- Autentificare completă

## Instalare

```bash
git clone https://github.com/tu-user/nutriplan-django.git
cd nutriplan-django
cp env/.env.example .env
# editează .env cu SECRET_KEY, email etc.
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Tehnologii

Django 5
Bootstrap 5
Chart.js
python-decouple
Gmail SMTP
