"""Module implements methods needed to perform dump related operations."""

import os
import sys
import shlex
import socket
import logging
import datetime
import shutil

from subprocess import Popen, PIPE
from pathlib import Path
from typing import Union
from hurry.filesize import size, si

from .helpers import env_exists


class MongoDump:
    """Dumps Mongo database and prepares bson files for the transfer.

    Attributes:
        mongo_uri: connection string in format

        "mongodb://user:password@server:[port]/?replicaSet=NAME&authSource=admin"

        output_folder: path to where local dump will be performed
    """

    def __init__(self):
        """Initializes MongoDump with connection URI."""
        self.mongo_uri = os.getenv('MONGO_URI')

        if not env_exists(self.mongo_uri):
            logging.error(
                'No MongoDB connection URI provided. Nothing to do - exiting now.'
            )
            sys.exit(1)

        mongo_output_folder = os.getenv('MONGO_OUTPUT_FOLDER')

        if not env_exists(mongo_output_folder):
            mongo_output_folder = 'dump'
        self.output_folder = Path.absolute(Path(mongo_output_folder))

    def _strip_mongo_uri(self) -> list:
        """Strips mongo_uri to get list of mongodb servers provided.

        Returns:
            mongo_srv_list: list, contains tuples in a way (mongo_host:str, *mongo_port:str)
        """
        try:
            mongo_srv_string = (str(self.mongo_uri).split('/'))[2]
        except IndexError:
            mongo_srv_string = str(self.mongo_uri)
        try:
            mongo_srv_string_no_creds = (mongo_srv_string.split('@'))[1]
        except IndexError:
            mongo_srv_string_no_creds = mongo_srv_string
        mongo_srv_list = [
            tuple(location.split(':'))
            for location in mongo_srv_string_no_creds.split(',')
        ]
        return mongo_srv_list

    def _check_mongo_socket(self) -> bool:
        """Checks if at least one of given servers in mongo_uri is live.

        Returns:
            True: for the first alive server
            False: if none of given servers are live
        """
        for mongo_srv in self._strip_mongo_uri():
            mongo_host = str(mongo_srv[0])
            mongo_port = 27017
            if len(mongo_srv) == '2':
                mongo_port = (int(mongo_srv[1]))
            location = (mongo_host, mongo_port)
            with socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM) as mongo_socket:
                try:
                    connection_state = mongo_socket.connect_ex(location)
                    if connection_state == 0:
                        return True
                except socket.gaierror:
                    logging.error('MongoDB is not serving at "%s" port "%s".',
                                 mongo_host, str(mongo_port))
        return False

    def _get_dump_size(self) -> Union[str, bool]:
        """Calculates the size for the dump folder and returns it in SI value.

        Returns:
            folder_size: str, folder size in SI
            'False' in case of failure
        """
        try:
            summary = sum(f.stat().st_size
                          for f in Path(self.output_folder).rglob('*')
                          if f.is_file())
        except os.error:
            return False
        folder_size = size(summary, system=si)
        logging.info('Dump folder is stored at "%s" and "%s" large.',
                     self.output_folder, folder_size)
        return folder_size

    def _rename_dump(self) -> Union[str, bool]:
        """Renames temporary dump folder by adding current date.

        Returns:
            folder_name: str, new folder name
        """
        dump_folder_name = f'{str(self.output_folder)}-{str(datetime.date.today())}'
        if Path(dump_folder_name).is_dir():
            logging.warning('Dump folder "%s" already exists. Removing now.',
                            dump_folder_name)
            shutil.rmtree(dump_folder_name)
        try:
            shutil.move(str(self.output_folder), dump_folder_name)
            logging.info('Dump folder renamed and stored at "%s"',
                         dump_folder_name)
        except os.error as error_msg:
            logging.error(error_msg)
            return False
        return dump_folder_name

    def dump_db(self) -> bool:
        """Performs dump of the database to the local folder.

        Returns:
            The result of dump command.
            True: if successful
            False: in case of failure
        """
        if self._check_mongo_socket():
            cmd = f'mongodump --uri="{self.mongo_uri}" --gzip --out {self.output_folder}'
            args = shlex.split(cmd)
            dump_process = Popen(args, stdout=PIPE)
            with dump_process.stdout:
                for line in iter(dump_process.stdout.readline, b''):
                    dump_process_output = bytes(line).decode('utf-8').strip(
                        '\n')
                    logging.info(dump_process_output)
            exit_code = dump_process.wait()
            if exit_code == 0:
                return True
        return False

    def cleanup(self) -> bool:
        """Performs cleanup steps on exist or failure.

        Returns:
            True: if successful
            False: in case of failure
        """
        try:
            dump_folder_name = f'{str(self.output_folder)}-{str(datetime.date.today())}'
            if Path(dump_folder_name).is_dir():
                logging.warning(
                    'Performing cleanup steps - "%s" removed.',
                    dump_folder_name)
                shutil.rmtree(dump_folder_name)
            if Path(str(self.output_folder)).is_dir():
                logging.warning(
                    'Performing cleanup steps - "%s" removed.',
                    str(self.output_folder))
                shutil.rmtree(dump_folder_name)
            return True
        except OSError:
            logging.error('Application failed to perform cleanup steps')
            return False

    def exec(self) -> dict:
        """Wraps all class methods for single start

        Returns:
            result: dict, result of dump operations as dictionary
        """
        dump_state = self.dump_db()
        if dump_state:
            result = {
                'dump': str(dump_state),
                'size': self._get_dump_size(),
                'path': self._rename_dump()
            }
        else:
            result = {'dump': str(dump_state)}
        logging.debug(str(result))
        return result
