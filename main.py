#!/bin/env python3
"""mongo-dump is a S3 storage compatible backup utility for MongoDB."""


from pathlib import Path
# from dotenv import load_dotenv
from mongodump_s3 import log, startup_options

log()

# ToDo parse dump result here
# ToDo parse upload result here


# def load_env(env_file):
#     env_path = Path(env_file)
#     load_dotenv(dotenv_path=env_path)


def main():
    """Combines all moving parts together and sends notifications if needed."""

    # env_list = 'dev.env'
    #
    # load_env(env_list)  # FixMe
    #
    # result = MongoDump().start()
    #
    # dump_path = str(result['path'])
    #
    # dump_path_parent = str(Path(dump_path).parent)
    #
    # cloud = S3(create_buckets=True)
    #
    # cloud.upload_local_folder(dump_path, dump_path_parent)
    #
    # report = Notifications(str(result))
    #
    # report.send_telegram_notification()

    # report.send_email_notification()



if __name__ == '__main__':
    startup_options()
