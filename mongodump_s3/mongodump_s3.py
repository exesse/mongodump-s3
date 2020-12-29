"""Main module contains functions need by mongodump-s3 package."""

import os
import argparse
import logging

__version__ = '0.0.1-dev'


def env_exists(env_variable: str) -> bool:
    """Validates if env variable was provided and is not an empty string.

    Args:
        env_variable: str, name of the env variable

    Returns:
        True: if env provide and not an empty string
        False: if env not provided or an empty string
    """
    if env_variable is not None and env_variable != '':
        return True
    return False


def log() -> None:
    """Setups logging to stdout with logging level INFO."""
    return logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def str_to_dict(argument_string: str) -> dict:
    result = {}
    separate_kv = argument_string.split(' ')
    for kv in separate_kv:
        k, v = kv.split('=')
        result[k] = v
    return result


def startup_options():
    """Function implements CLI interface."""

    cli_parser = argparse.ArgumentParser(prog='mongodump-s3',
                                         usage='%(prog)s <options>',
                                         description='Export the content of a running server into .bson files'
                                                     ' and uploads to provided S3 compatible storage.'
                                                     ' By default loads required settings from environment'
                                                     ' variables.',
                                         add_help=False)

    # Section: general options
    general = cli_parser.add_argument_group('general options')
    general.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='print usage.')

    general.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}',
                         help='print the tool version and exit.')

    # Section: output options
    output = cli_parser.add_argument_group('output options')
    output.add_argument('-b', '--bucket', action='store', metavar='<S3 Bucket>',
                        help='S3 bucket name for upload, defaults to \'mongodump\'')
    output.add_argument('-o', '--out', action='store', metavar='<folder>',
                        help='output directory, defaults to \'dump\'.')

    # Section: uri options
    uri = cli_parser.add_argument_group('uri options')
    uri.add_argument('-u', '--uri', action='store', type=str, metavar='<uri>',
                     help='mongodb uri connection string.'
                     ' See official description here'
                     ' https://docs.mongodb.com/manual/reference/connection-string')

    # Section: environmental options
    env = cli_parser.add_argument_group('environmental options')
    env.add_argument('-e', '--env', action='store', type=str, metavar='<env-file>',
                     help='path to file containing environmental variables.')

    # Section: cloud storage options
    cloud_storage = cli_parser.add_argument_group('cloud storage options')
    cloud_storage.add_argument('--azure', action='store', type=str, metavar='<azure_storage_connection_string>',
                               help='connection string for storage account provided by Azure.')

    cloud_storage.add_argument('--aws', action='store', type=str,
                               metavar='<aws_access_key_id=value>'
                               ' <aws_secret_access_key=value> <aws_region=value>',
                               help='AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION properties'
                               ' provided by Amazon Web Services IAM. '
                               'AWS_REGION defaults to \'us-west-2\' if not specified.')
    cloud_storage.add_argument('--gcp', action='store', type=str,
                               metavar='<google_application_credentials=value> <google_region=value>',
                               help='path to service account file and optional Google Cloud Region.'
                               ' GOOGLE_REGION defaults to \'us-multiregion\' if not specified.')

    # Section: notification options
    notification = cli_parser.add_argument_group('notification options')
    notification.add_argument('--email', action='store', metavar='<user@example.com>',
                              help='email address which to notify upon the result.')
    notification.add_argument('--smtp', action='store', metavar='<mail-server.example.com>',
                              help='SMTP relay server to use, defaults to \'localhost\'.')
    notification.add_argument('--telegram', action='store', type=str,
                              metavar='<telegram_token> <telegram_chat_id>',
                              help='Telegram API token and chat id to be used for notification. '
                                   ' See more: https://core.telegram.org/bots/api.')

    # Section: feedback
    feedback = cli_parser.add_argument_group('Feedback')
    feedback.add_argument('Please star project on GitHub: https://github.com/exesse/mongodump-s3')
    feedback.add_argument('Email bug reports, questions, discussions to mailto:hi@exesse.org')

    return cli_parser.parse_args()


def mask_env(scope: str = 'all') -> bool:
    try:
        if scope == 'cloud':
            os.environ['AZURE_STORAGE_CONNECTION_STRING'] = ''
            os.environ['AWS_REGION'] = ''
            os.environ['AWS_ACCESS_KEY_ID'] = ''
            os.environ['AWS_SECRET_ACCESS_KEY'] = ''
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''
            os.environ['GOOGLE_REGION'] = ''
            return True
        else:
            os.environ['MONGO_URI'] = ''
            os.environ['MONGO_OUTPUT_FOLDER'] = ''
            os.environ['MONGO_DUMP_BUCKET'] = ''
            os.environ['EMAIL'] = ''
            os.environ['SMTP_RELAY'] = ''
            os.environ['TELEGRAM_TOKEN'] = ''
            os.environ['TELEGRAM_CHAT_ID'] = ''
            os.environ['AZURE_STORAGE_CONNECTION_STRING'] = ''
            os.environ['AWS_REGION'] = ''
            os.environ['AWS_ACCESS_KEY_ID'] = ''
            os.environ['AWS_SECRET_ACCESS_KEY'] = ''
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''
            os.environ['GOOGLE_REGION'] = ''
            return True
    except OSError as error_response:
        logging.error(error_response)
    return False


def mongodump_s3_app():
    options = startup_options()
    if options.uri:
        pass  # TODO
