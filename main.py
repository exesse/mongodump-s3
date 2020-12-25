"""mongo-dump is a S3 storage compatible backup utility for MongoDB."""


from pathlib import Path
from dotenv import load_dotenv
from mongo_dump_s3 import MongoDump, S3, Notifications, log

log()


# ToDo S3 upload here
# ToDo parse dump result here
# ToDo parse upload result here


def load_env(env_file):
    env_path = Path(env_file)
    load_dotenv(dotenv_path=env_path)


def main():
    """Combines all moving parts together and sends notifications if needed."""

    env_list = 'dev.env'

    load_env(env_list)  # FixMe

    result = str(MongoDump().start())

    cloud = S3(create_buckets=True)

    cloud.upload_local_folder('/tmp/mongo-dump/hannover-2020-12-24', '/tmp/mongo-dump/')

    # report = Notifications(result)

    # report.send_telegram_notification()
    #
    # # report.send_email_notification()


if __name__ == '__main__':
    main()
