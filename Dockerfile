# Bruk en stabil versjon av Python
FROM python:3.11

# Sett arbeidsmappen i containeren
WORKDIR /app

# Kopier alle filer fra prosjektmappen til containeren
COPY . .

# Installer avhengigheter
RUN pip install --no-cache-dir flask requests

# Eksponer port 5000 for Flask-serveren
EXPOSE 5000

# Start appen når containeren kjører
CMD ["python", "app.py"]
