FROM python:3.12-slim

# Создаем пользователя app
RUN groupadd -r app && useradd -r -g app app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Меняем владельца файлов на пользователя app
RUN chown -R app:app /app

# Переключаемся на пользователя app
USER app

# Expose порт
EXPOSE 8000

# Health check
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
