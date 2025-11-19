FROM python:3.12-slim

WORKDIR /code

# Устанавливаем необходимые системные пакеты
RUN apt-get update && apt-get install -y build-essential

# Устанавливаем зависимости сервиса
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY app ./app
COPY tests ./tests

# По умолчанию запускаем uvicorn (для обычного сервера)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
