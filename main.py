"""mongo-dump is a S3 storage compatible backup utility for MongoDB."""

from pathlib import Path
from dotenv import load_dotenv
from mongo_dump import MongoDump, S3, Notifications


# ToDo S3 upload here
# ToDo parse dump result here
# ToDo parse upload result here


def load_env(env_file):
    env_path = Path(env_file)
    load_dotenv(dotenv_path=env_path)


def main(local=False):
    """Combines all moving parts together and sends notifications if needed."""

    if local:
        load_env('./dev.env')  # FixMe

    result = str(MongoDump().start())

    cloud = S3()

    cloud.create_storage_clients()

    report = Notifications(result)

    report.send_telegram_notification()

    report.send_email_notification()


if __name__ == '__main__':
    main(True)
