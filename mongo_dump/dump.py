"""Module implements methods needed to perform dump related operations."""

import os
import shlex
import logging
from subprocess import Popen, PIPE

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


class MongoDump:
    """Dumps Mongo database and prepares bson files for the transfer.

    Attributes:
        mongo_uri: connection string in format mongodb://server:[port]/?replicaSet=NAME&authSource=admin
    """

    def __init__(self):
        """Initializes MongoDump with connection URI."""
        self.mongo_uri = os.getenv('MONGO_URI')
        self.output_folder = os.getenv('OUTPUT_FOLDER')
        if self.output_folder is None:
            self.output_folder = 'dump'

    def dump_db(self) -> int:
        """Performs dump of the database to the local folder.

        Returns:
            exit_code - the result of dump command
        """
        cmd = f'/bin/mongodump --uri="{self.mongo_uri}" --gzip --out ./{self.output_folder}'
        args = shlex.split(cmd)
        dump_process = Popen(args, stdout=PIPE)
        with dump_process.stdout:
            for line in iter(dump_process.stdout.readline, b''):
                dump_process_output = line.decode('utf-8').strip('\n')
                logging.info(dump_process_output)
        exit_code = dump_process.wait()
        return exit_code
