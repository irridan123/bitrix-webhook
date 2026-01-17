from flask import Flask, request, jsonify
import asyncio
from telegram import Bot
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация
TELEGRAM_TOKEN = "7621205041:AAF7VtIQJjjbMCwS5Udz8utHVH1B0aFtqk0"
BITRIX_APP_TOKEN = "4176wq9roeiyt0oc1y9epxxj9g49bqi6"
YOUR_TELEGRAM_CHAT_ID = "1389473957"  

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_notification(message):
    """Отправка уведомления в Telegram"""
    try:
        await bot.send_message(chat_id=YOUR_TELEGRAM_CHAT_ID, text=message)
        logger.info(f"Уведомление отправлено: {message}")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

@app.route('/webhook/bitrix', methods=['POST'])
def bitrix_webhook():
    """Обработчик исходящих вебхуков от Bitrix24"""
    try:
        data = request.json
        logger.info(f"Получен webhook от Bitrix24: {data}")
        
        # Проверка токена приложения
        auth_data = data.get('auth', {})
        app_token = auth_data.get('application_token', '')
        
        if app_token != BITRIX_APP_TOKEN:
            logger.warning(f"Неверный токен: {app_token}")
            return jsonify({"error": "Invalid token"}), 403
        
        # Получаем информацию о событии
        event = data.get('event', 'Неизвестное событие')
        fields_after = data.get('data', {}).get('FIELDS_AFTER', {})
        
        # Формируем сообщение для Telegram
        message = f"🔔 Событие из Bitrix24\n\n"
        message += f"Тип: {event}\n"
        message += f"Данные: {fields_after}\n"
        message += f"Домен: {auth_data.get('domain', 'N/A')}"
        
        # Отправляем уведомление в Telegram
        asyncio.run(send_telegram_notification(message))
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности"""
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def index():
    """Главная страница"""
    return """
    <h1>Bitrix24 Webhook Handler</h1>
    <p>Сервер работает!</p>
    <p>Endpoint для Bitrix24: <code>/webhook/bitrix</code></p>
    """, 200

if __name__ == '__main__':
    # Запуск Flask на порту 80
    app.run(host='0.0.0.0', port=80, debug=False)