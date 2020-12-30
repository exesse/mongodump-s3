"""Main module contains functions needed by mongodump-s3 package."""

import os
import argparse
import logging

from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from .s3 import S3
from .dump import MongoDump
from .notifications import Notifications

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class MongoDumpS3:
    """Implement CLI and handles command execution.

    Attributes:
        options:
    """

    __version__ = '0.0.1-dev'

    def __init__(self):
        """Inits MongoDumpS3 with startup options."""
        self.options = self._startup_options()

    @classmethod
    def _startup_options(cls):
        """Function implements CLI interface."""

        cli_parser = argparse.ArgumentParser(prog='mongodump-s3',
                                             usage='%(prog)s <options>',
                                             description='Export the content of a running server into .bson files'
                                                         ' and uploads to provided S3 compatible storage.'
                                                         ' By default loads required settings from environment'
                                                         ' variables.',
                                             epilog='Email bug reports, questions, discussions'
                                                    ' to mailto:hi@exesse.org.'
                                                    ' Please star project on GitHub:'
                                                    ' https://github.com/exesse/mongodump-s3',
                                             add_help=False)

        # Section: general options
        general = cli_parser.add_argument_group('general options')
        general.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='print usage.')

        general.add_argument('-v', '--version', action='version', version=f'%(prog)s {cls.__version__}',
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

        return cli_parser.parse_args()

    @staticmethod
    def _mask_env(scope: str = 'all') -> bool:
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

    @staticmethod
    def _str_to_dict(argument_string: str) -> dict:
        result = {}
        separate_kv = argument_string.split(' ')
        for kv in separate_kv:
            k, v = kv.split('=')
            result[k] = v
        return result

    @staticmethod
    def _set_env(env_kwargs: dict) -> bool:
        try:
            for key in env_kwargs:
                os.environ[str(key).upper()] = str(env_kwargs[key])
        except OSError as error_response:
            logging.error(error_response)
            logging.error('Application was not able to set env variables.'
                          ' Please report the bug to mailto:hi@exesse.org')
            return False
        return True

    @staticmethod
    def _debug_env() -> None:
        logging.debug('MONGO_URI set to "%s"', os.getenv('MONGO_URI'))
        logging.debug('MONGO_OUTPUT_FOLDER set to "%s"', os.getenv('MONGO_OUTPUT_FOLDER'))
        logging.debug('MONGO_DUMP_BUCKET set to "%s"', os.getenv('MONGO_DUMP_BUCKET'))
        logging.debug('EMAIL set to "%s"', os.getenv('EMAIL'))
        logging.debug('SMTP_RELAY set to "%s"', os.getenv('SMTP_RELAY'))
        logging.debug('TELEGRAM_TOKEN set to "%s"', os.getenv('TELEGRAM_TOKEN'))
        logging.debug('TELEGRAM_CHAT_ID set to "%s"', os.getenv('TELEGRAM_CHAT_ID'))
        logging.debug('AZURE_STORAGE_CONNECTION_STRING set to "%s"', os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
        logging.debug('AWS_REGION set to "%s"', os.getenv('AWS_REGION'))
        logging.debug('AWS_ACCESS_KEY_ID set to "%s"', os.getenv('AWS_ACCESS_KEY_ID'))
        logging.debug('AWS_SECRET_ACCESS_KEY set to "%s"', os.getenv('AWS_SECRET_ACCESS_KEY'))
        logging.debug('GOOGLE_APPLICATION_CREDENTIALS set to "%s"', os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
        logging.debug('GOOGLE_REGION set to "%s"', os.getenv('GOOGLE_REGION'))

    def prepare_app_env(self) -> bool:

        # Clear env if env-file provided manually
        if self.options.env:
            env_file_path = Path(self.options.env)
            if env_file_path.is_file():
                load_dotenv(dotenv_path=env_file_path)
                self._debug_env()
                return True
            logging.error('Provided env file "%s" does not exists. Please check.', self.options.env)
            return False

        # Clear env variables if s3 properties provided manually
        if self.options.azure or self.options.aws or self.options.gcp:
            if self._mask_env('cloud'):
                if self.options.azure:
                    azure = {'AZURE_STORAGE_CONNECTION_STRING': self.options.azure}
                    if not self._set_env(azure):
                        return False
                if self.options.gcp:
                    gcp = self._str_to_dict(self.options.gcp)
                    if not self._set_env(gcp):
                        return False
                if self.options.aws:
                    aws = self._str_to_dict(self.options.aws)
                    if not self._set_env(aws):
                        return False

        # Simple options that don't need mask usage
        if self.options.bucket:
            bucket = {'MONGO_DUMP_BUCKET': self.options.bucket}
            if not self._set_env(bucket):
                return False
        if self.options.out:
            out = {'MONGO_OUTPUT_FOLDER': self.options.out}
            if not self._set_env(out):
                return False
        if self.options.uri:
            uri = {'MONGO_URI': self.options.uri}
            if not self._set_env(uri):
                return False
        if self.options.email:
            email = {'EMAIL': self.options.email}
            if not self._set_env(email):
                return False
        if self.options.smtp:
            smtp = {'SMTP_RELAY': self.options.smtp}
            if not self._set_env(smtp):
                return False
        if self.options.telegram:
            telegram = self._str_to_dict(self.options.telegram)
            if not self._set_env(telegram):
                return False

        self._debug_env()
        return True
    
    def exec(self):
        bang = '\U0001F4A5'
        dump = '\U0001F9BA'
        time = '\U0001F312'
        fail = '\U0001F4A9'
        start = datetime.now()
        if self.prepare_app_env():
            failure = '%s mongodump-s3 failed. Please see logs.' % fail
            dump = MongoDump()
            dump_result = dump.exec()

            if dump_result['dump'] == 'False':
                Notifications(failure)
                dump.cleanup()
                return False

            dump_size = dump_result['size']
            dump_path = dump_result['path']
            dump_path_parent = str(Path(dump_path).parent)

            s3_upload = S3()
            s3_upload_result = s3_upload.upload_local_folder(dump_path, dump_path_parent)

            if s3_upload_result:
                end = str(datetime.now() - start)[:-7]
                success = f'{bang} mongodump-s3 finished the job.' \
                          f'\n{dump}Dump size is {dump_size}.\n{time}Processing time is {end}'
                Notifications(success)
                dump.cleanup()
                return True
            dump.cleanup()
            return False

# TODO refactor old modules, remove trailing dots and add '' for long envs in help,
#  pack as pypi, write README, fix doc-strings