"""mongo-dump is a S3 storage compatible backup utility for MongoDB."""

import os
import logging
from pathlib import Path
from socket import gaierror
from dotenv import load_dotenv
from mongo_dump import TelegramNotifications, EmailNotifications, MongoDump

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def send_telegram_notification(msg: str) -> None:
    """"Handler for Telegram notifications.

    Attributes:
        msg: str, text body to be send

    Returns:
        None
    """
    if os.getenv('TELEGRAM_CHAT_ID') and os.getenv('TELEGRAM_TOKEN'):
        logging.info('Sending telegram notification to "%s".', os.getenv('TELEGRAM_CHAT_ID'))
        TelegramNotifications().send_msg(msg)


def send_email_notification(msg: str) -> None:
    """Handler for Email notifications.

    Attributes:
        msg: str, text body to be sent

    Returns:
        None
    """
    if os.getenv('EMAIL') and os.getenv('SMTP_RELAY'):
        try:
            EmailNotifications().send_email(msg)
            logging.info('Sending email to "%s" via smtp relay "%s"',
                         os.getenv('EMAIL'), os.getenv('SMTP_RELAY'))
        except gaierror:
            logging.error('smtp relay server "%s" is not available. Please check.',
                          os.getenv('SMTP_RELAY'))


def perform_mongodb_dump() -> dict:
    """Handler for MongoDump class.

    Returns:
        A dictionary with the result values for operations.
        An example:

        {
        'dump': True,
        'size': '2K',
        'path': '/tmp/mongo-dump/smoke-2020-12-21'
        }
    """
    mongodb_uri = os.getenv('MONGO_URI')
    if mongodb_uri is None or mongodb_uri == '':
        logging.error('No MongoDB connection URI provided. Nothing to do - exiting now.')
        exit(1)
    svc = MongoDump()
    mongo_dump_response = svc.start()
    return mongo_dump_response


def main():
    """Combines all moving parts together and sends notifications if needed."""

    # FixME Lets explicitly load environment variables in dev
    env_path = Path('./dev.env')
    load_dotenv(dotenv_path=env_path)

    result = str(perform_mongodb_dump())

    send_email_notification(result)

    send_telegram_notification(result)

    # ToDo S3 upload here
    # ToDo parse dump result here
    # ToDo parse upload result here


if __name__ == '__main__':
    main()
