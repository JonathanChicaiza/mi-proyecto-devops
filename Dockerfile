FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY app/ .

EXPOSE 5000

CMD ["python", "app.py"]