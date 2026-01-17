from flask import Flask, request, jsonify
import asyncio
from telegram import Bot
import logging
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация
TELEGRAM_TOKEN = "7621205041:AAF7VtIQJjjbMCwS5Udz8utHVH1B0aFtqk0"
BITRIX_APP_TOKEN = "4176wq9roeiyt0oc1y9epxxj9g49bqi6"
YOUR_TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # Замените на ваш chat_id

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
        # Bitrix24 может отправлять данные в разных форматах
        content_type = request.content_type or ''
        logger.info(f"Content-Type: {content_type}")
        
        # Получаем данные в зависимости от Content-Type
        if 'application/json' in content_type:
            data = request.json
        else:
            # Для application/x-www-form-urlencoded или multipart/form-data
            data = request.form.to_dict()
            # Если данных нет в form, пробуем получить из args (GET параметры)
            if not data:
                data = request.args.to_dict()
            # Если данные пришли как строка JSON в одном из полей
            for key, value in list(data.items()):
                try:
                    data[key] = json.loads(value)
                except:
                    pass
        
        logger.info(f"Получен webhook от Bitrix24: {data}")
        
        # Проверка токена приложения (если есть в данных)
        auth_data = data.get('auth', {})
        if isinstance(auth_data, str):
            try:
                auth_data = json.loads(auth_data)
            except:
                auth_data = {}
        
        app_token = auth_data.get('application_token', '')
        
        # Если токен есть, проверяем его
        if app_token and app_token != BITRIX_APP_TOKEN:
            logger.warning(f"Неверный токен: {app_token}")
            return jsonify({"error": "Invalid token"}), 403
        
        # Получаем информацию о событии
        event = data.get('event', 'Неизвестное событие')
        
        # Формируем сообщение для Telegram
        message = f"🔔 Событие из Bitrix24\n\n"
        message += f"Тип: {event}\n"
        message += f"Данные:\n{json.dumps(data, indent=2, ensure_ascii=False)[:500]}"
        
        # Отправляем уведомление в Telegram
        asyncio.run(send_telegram_notification(message))
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}", exc_info=True)
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
    <p>Status: <a href="/health">Health Check</a></p>
    """, 200

if __name__ == '__main__':
    # Запуск Flask на порту 80
    app.run(host='0.0.0.0', port=80, debug=False)