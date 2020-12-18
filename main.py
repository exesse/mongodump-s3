import os
from mongo_dump import TelegramNotifications, EmailNotifications


if __name__ == '__main__':
    MSG = '\U0001F4A5 test msg'

    print(os.getenv('EMAIL'))
    print(os.getenv('MONGO_URI'))
    print(os.getenv('TELEGRAM_CHAT_ID'))
    print(os.getenv('TELEGRAM_TOKEN'))
    print(os.getenv('SMTP_RELAY'))

    # Notifications TEST
    telegram = TelegramNotifications()
    telegram.send_msg(MSG)

    smtp = EmailNotifications()
    smtp.send_email(MSG)
