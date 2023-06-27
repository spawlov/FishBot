import os

from dotenv import load_dotenv, find_dotenv

from bots.tg_bot import run_bot
from db.redis import get_database_connection


def main():
    load_dotenv(find_dotenv())
    base_url = os.getenv('API_BASE_URL')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    db = get_database_connection(redis_host, redis_port, redis_password)

    run_bot(
        os.getenv('SHOP_BOT'),
        base_url,
        client_id,
        client_secret,
        db,
        os.getenv('LOGGER_BOT_TOKEN'),
        os.getenv('LOGGER_CHAT_ID'),
    )


if __name__ == '__main__':
    main()
