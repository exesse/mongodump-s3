"""Module contains cloud S3 storage related methods."""


import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


# ToDo Write a check for each cloud provider if the bucket with given name exists
# ToDo If doesn't exists create the bucket
# ToDo Write methods for each provider with async upload of a file to the bucket
# ToDo Write handler that uploads folder for each provider


class S3:
    """Implements S3 storage related operations."""

    def __init__(self, env_path: str):
        """Initializes class S3 with bucket name."""
        load_dotenv(dotenv_path=env_path)
        self.s3_bucket = os.getenv('BUCKET')

    def __make_azure_client(self):
        """Creates Azure client with provided credentials.

        Returns:
            False: if not connection string provided
            azure_s3: bucket object that will be used to operate with Azure API
        """
        azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if azure_connection_string is not None and azure_connection_string != '':
            logging.info('Azure connection parameters found.')
            azure_connection = BlobServiceClient.from_connection_string(azure_connection_string)
            azure_s3 = azure_connection.get_container_client(self.s3_bucket)
            try:
                #ToDo test for name taken
                azure_s3.create_container()
            except ResourceExistsError:
                logging.info('Container "%s" already exists.', self.s3_bucket)
            return azure_s3
        return False

    def __make_aws_client(self):
        """Creates AWS boto3 client with provided credentials.

        Returns:
            False: if not connection string provided
            aws_s3: bucket object that will be used to operate with Amazon API
        """
        aws_region = os.getenv('AWS_REGION')
        if aws_region is None or aws_region == '':
            aws_region = 'us-west-2'
        logging.info('"%s" will be used as AWS region', aws_region)
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        if aws_access_key_id is not None and aws_access_key_id != '':
            if aws_secret_access_key is not None and aws_secret_access_key != '':
                logging.info('AWS connection parameters found.')
                try:
                    aws_s3 = boto3.client('s3', region_name=aws_region)
                    location = {'LocationConstraint': aws_region}
                    aws_s3.create_bucket(Bucket=self.s3_bucket, CreateBucketConfiguration=location)
                except ClientError as exc:
                    if exc.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                        logging.info('Container "%s" already exists.', self.s3_bucket)
                    else:
                        logging.error(exc)
                        return False
                return aws_s3
        return False

    def create_storage_clients(self):
        """Creates client connections from env for the cloud to be used."""
        providers = dict()
        azure_s3 = self.__make_azure_client()
        if azure_s3:
            providers['azure'] = azure_s3
        aws_s3 = self.__make_aws_client()
        if aws_s3:
            providers['aws'] = aws_s3
        logging.info(providers)
        return providers


if __name__ == '__main__':
    env = Path('/home/intern.chipcytometry.com/kulbatski/Bin/mongo-dump/dev.env')
    Azure = S3(env)

    Azure.create_storage_clients()
