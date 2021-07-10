import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    homework_statuses = requests.get(url=url, params=params, headers=headers)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text='Done')


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            homework_req = get_homeworks(current_timestamp)
            if homework_req.get('homeworks'):
                send_message(parse_homework_status(
                    homework_req.get('homework')[0])
                )
            current_timestamp = homework_req.get('current_date')
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(massage)s'
)

if __name__ == '__main__':
    main()
