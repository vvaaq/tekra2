FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем пакеты и устанавливаем системные библиотеки
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000"]