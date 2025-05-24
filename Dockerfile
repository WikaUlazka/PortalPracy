# Użyj oficjalnego obrazu Pythona
FROM python:3.11-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki projektu
COPY . .

# Zainstaluj zależności
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Otwórz port (dla developera)
EXPOSE 8000

# Uruchom serwer Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
