"""Module implements methods needed to perform dump related operations."""

import os
import shlex
import logging
import datetime
import shutil
from subprocess import Popen, PIPE
from pathlib import Path
from typing import Union
from hurry.filesize import size, si

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class MongoDump:
    """Dumps Mongo database and prepares bson files for the transfer.

    Attributes:
        mongo_uri: connection string in format

        "mongodb://user:password@server:[port]/?replicaSet=NAME&authSource=admin"

    """

    def __init__(self):
        """Initializes MongoDump with connection URI."""
        self.mongo_uri = os.getenv('MONGO_URI')
        output_folder_name = os.getenv('OUTPUT_FOLDER')
        if output_folder_name is None:
            output_folder_name = 'dump'
        self.output_folder = f'/tmp/mongo-dump/{output_folder_name}'

    def dump_db(self) -> bool:
        """Performs dump of the database to the local folder.

        Returns:
            The result of dump command.
            'True' if successful
            'False' in case of failure
        """
        cmd = f'/bin/mongodump --uri="{self.mongo_uri}" --gzip --out {self.output_folder}'
        args = shlex.split(cmd)
        dump_process = Popen(args, stdout=PIPE)
        with dump_process.stdout:
            for line in iter(dump_process.stdout.readline, b''):
                dump_process_output = line.decode('utf-8').strip('\n')
                logging.info(dump_process_output)
        exit_code = dump_process.wait()
        if exit_code == 0:
            return True
        return False

    def get_dump_size(self) -> Union[str, bool]:
        """Calculates the size for the dump folder and returns it in SI value.

        Returns:
            folder_size: str, folder size in SI
            'False' in case of failure
        """
        try:
            summary = sum(f.stat().st_size for f
                          in Path(self.output_folder).rglob('*') if f.is_file())
        except os.error:
            return False
        folder_size = size(summary, system=si)
        logging.info('Dump folder is stored at "%s" and "%s" large.',
                     self.output_folder, folder_size)
        return folder_size

    def rename_dump(self) -> Union[str, bool]:
        """Renames temporary dump folder by adding current date.

        Returns:
            folder_name: str, new folder name
        """
        dump_folder_name = f'{str(self.output_folder)}-{str(datetime.date.today())}'
        if Path(dump_folder_name).is_dir():
            logging.warning('Dump folder "%s" already exists. Removing now.', dump_folder_name)
            shutil.rmtree(dump_folder_name)
        try:
            shutil.move(self.output_folder, dump_folder_name)
            logging.info('Dump folder renamed and stored at "%s"', dump_folder_name)
        except os.error as error_msg:
            logging.error(error_msg)
            return False
        return dump_folder_name

    def start(self) -> dict:
        """Wraps all class methods for single start

        Returns:
            result: dict, result of dump operations as dictionary
        """
        result = {
            'dump': self.dump_db(),
            'size': self.get_dump_size(),
            'path': self.rename_dump()
        }
        logging.debug(str(result))
        return result
