"""mongo-dump is a S3 storage compatible backup utility for MongoDB."""

from pathlib import Path
from dotenv import load_dotenv
from mongo_dump import MongoDump, S3, Notifications


def main():
    """Combines all moving parts together and sends notifications if needed."""

    # # FixME Lets explicitly load environment variables in dev
    env_path = Path('./dev.env')
    load_dotenv(dotenv_path=env_path)

    result = str(MongoDump().start())

    # cloud = S3()
    #
    # cloud.create_storage_clients()

    # send_email_notification(result)
    #
    # send_telegram_notification(result)

    SEND = Notifications(result)

    SEND.send_telegram_notification()

    SEND.send_email_notification()


    # ToDo S3 upload here
    # ToDo parse dump result here
    # ToDo parse upload result here


if __name__ == '__main__':
    main()
