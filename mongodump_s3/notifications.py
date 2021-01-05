"""Module implements various notification methods."""

import os
import smtplib
import logging

from socket import gaierror
from email.message import EmailMessage
from requests import post

from .helpers import env_exists


class Notifications:
    """Handles notifications requests.

    Attributes:
        message: str, plain text msg that will be send
    """

    def __init__(self, message: str) -> None:
        """Initializes class Notifications.

        Args:
            message: str, plain text body that will be sent
        """
        self.message = message
        self.send_email_notification()
        self.send_telegram_notification()

    def send_telegram_notification(self) -> bool:
        """"Handler for Telegram notifications.

        Returns:
            Fail: if no env variables were provided
            True: if environment values exists and msg was sent
        """
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        telegram_token = os.getenv('TELEGRAM_TOKEN')

        if env_exists(telegram_chat_id) and env_exists(telegram_token):
            telegram_send_message = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
            text_body = {'chat_id': telegram_chat_id, 'text': self.message}
            try:
                post(telegram_send_message, text_body).json()
                logging.info('Telegram notification sent to "%s".',
                             telegram_chat_id)
                return True
            except ConnectionError as error_response:
                details = str(error_response).split(':')[0]
                logging.error(details)
        return False

    def send_email_notification(self) -> bool:
        """Handler for Email notifications.

        Returns:
            Fail: if no env variables were provided
            True: if environment values exists and msg was sent
        """
        email = os.getenv('EMAIL')
        smtp_relay = os.getenv('SMTP_RELAY')

        if env_exists(email):
            if not env_exists(smtp_relay):
                smtp_relay = 'localhost'
            try:
                msg = EmailMessage()
                msg['Subject'] = '\U0001F4D1 [mongo-dump] status report'
                msg['From'] = 'mongo-dump@service.io'
                msg['To'] = email
                msg.set_content(self.message)
                with smtplib.SMTP(smtp_relay) as smtp:
                    smtp.send_message(msg)
                logging.info('Email was sent to "%s" via smtp relay "%s".',
                             email, smtp_relay)
                return True
            except gaierror:
                logging.error(
                    'smtp relay server "%s" is not available. Please check.',
                    smtp_relay)
            except OSError:
                logging.error(
                    'smtp relay server name "%s" could not be resolved over DNS. Please check.',
                    smtp_relay)
        return False
