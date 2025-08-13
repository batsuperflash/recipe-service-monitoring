import requests
import time
import logging
import telegram

URL = "http://127.0.0.1:8001/api/health"
CHECK_INTERVAL = 60
RESPONSE_TIME_THRESHOLD = 1.0
TREND_CHECK_COUNT = 3

TELEGRAM_TOKEN = "123456789:AAExampleToken-YourBotTokenHere"
TELEGRAM_CHAT_ID = "-1001234567890"

bot = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(filename="monitor.log",
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")

response_times = []

def send_telegram_message(message: str):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Ошибка при отправке Telegram сообщения: {e}")

def check_service():
    global response_times
    try:
        start = time.time()
        response = requests.get(URL)
        elapsed = time.time() - start

        if response.status_code == 200:
            logging.info(f"Сервис OK, время отклика: {elapsed:.2f} сек")
            print(f"[OK] Время отклика: {elapsed:.2f} сек")
            response_times.append(elapsed)
            if len(response_times) > TREND_CHECK_COUNT:
                response_times.pop(0)

            if elapsed > RESPONSE_TIME_THRESHOLD:
                warning_msg = f"[WARNING] Время отклика {elapsed:.2f} сек превысило порог {RESPONSE_TIME_THRESHOLD} сек"
                logging.warning(warning_msg)
                print(warning_msg)
                send_telegram_message(warning_msg)

            if len(response_times) == TREND_CHECK_COUNT:
                if all(response_times[i] < response_times[i+1] for i in range(TREND_CHECK_COUNT -1)):
                    trend_msg = "[TREND WARNING] Время отклика постепенно растёт."
                    logging.warning(trend_msg)
                    print(trend_msg)
                    send_telegram_message(trend_msg)

        else:
            error_msg = f"[ERROR] Код ответа: {response.status_code}"
            logging.error(error_msg)
            print(error_msg)
            send_telegram_message(error_msg)

    except requests.exceptions.RequestException as e:
        error_msg = f"[ERROR] Сервис недоступен. Ошибка: {e}"
        logging.error(error_msg)
        print(error_msg)
        send_telegram_message(error_msg)

def main():
    print("Запуск мониторинга сервиса...")
    while True:
        check_service()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
