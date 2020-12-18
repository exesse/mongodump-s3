"""Module implements methods needed to perform dump related operations."""

import os


class MongoDump:
    """Dumps Mongo database and prepares bson files for the transfer.

    Attributes:
        None

    """

    def __init__(self):
        """Initializes MongoDump with connection URI."""
        self.mongodb_uri = os.getenv()

    def dump_mongo(self) -> int:
        """

        Performs dump operations. Stores dump folder as {site}/{date} path.

        :rtype: int, exit code
        """
        cmd = f'/bin/mongodump --uri=mongodb://localhost:27017 --gzip'
        args = shlex.split(cmd)
        dump_process = Popen(args, stdout=PIPE)
        with dump_process.stdout:
            for line in iter(dump_process.stdout.readline, b''):
                dump_process_output = line.decode('utf-8').strip('\n')
                logging.info(dump_process_output)
        exit_code = dump_process.wait()
        return exit_code