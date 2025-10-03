#!/bin/bash
set -e

echo "🚀 Инициализация Ollama..."

# Сервис Ollama должен быть уже запущен через docker compose up -d
echo "⏳ Проверка статуса Ollama..."
docker compose exec -T ollama ollama list || true

# Подтягиваем модель codellama
echo "⬇️ Загрузка модели codellama..."
docker compose exec -T ollama ollama pull codellama

echo "✅ Модель готова!"
docker compose exec -T ollama ollama list
