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
PRACTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

bot = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(massage)s'
)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if homework_name is None:
        return 'Пришли пустые данные homework_name'
    if status is None:
        return 'Пришли пустые данные status'
    if status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif status == 'reviewing':
        verdict = 'Работа взята в ревью.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            url=PRACTIKUM_URL,
            params=params,
            headers=headers
        )
    except Exception as e:
        logging.error('Error at %s', 'division', exc_info=e)  # уточнить
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            homework_req = get_homeworks(current_timestamp)
            if homework_req.get('homeworks'):
                send_message(parse_homework_status(
                    homework_req.get('homework')[0])
                )
            if homework_req.get('current_date') is not None:
                current_timestamp = homework_req.get('current_date')
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logging.error('Error at %s', 'division', exc_info=e)  # уточнить
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
