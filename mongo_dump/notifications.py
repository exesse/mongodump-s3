"""Module implements various notification methods."""

import os
import requests


class TelegramNotifications:
    """Sends notifications using Telegram API.

    Attributes:
        token: bot token that will be used to send notifications
        chat_id: id of the chat where notifications will be send
    """

    def __init__(self, token, chat_id):
        """Initializes TelegramNotifications with token and chat_id."""
        # FIXME
        # token = os.getenv('TELEGRAM_TOKEN')
        # self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.token = token  # FIXME
        self.chat_id = chat_id  # FIXME
        self.telegram_send_message = send_message = f'https://api.telegram.org/bot{self.token}/sendMessage'

    def send_msg(self, message: str) -> dict:
        """Send messages using Telegram API calls.

        Arguments:
            message: str, text that will be send to the target user

        Returns:
            request method 'post' with data for a telegram api call
        """
        text_body = {'chat_id': self.chat_id, 'text': message}
        return requests.post(self.telegram_send_message, text_body).json()


class EmailNotifications:
    """Sends notifications using SMTP relay.

    Attributes:
    """

    def __init__(self):
        """Initializes EmailNotification with ."""
        pass
