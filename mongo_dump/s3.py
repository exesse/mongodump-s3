"""Module contains cloud S3 storage related methods."""


import os
import json
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import boto3
from botocore.exceptions import ClientError as AmazonClientError
from google.cloud import storage
from google.cloud.exceptions import ClientError as GoogleClientError
from mongo_dump import env_exists

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# ToDo 'Container' already exist for provider specific
# ToDo use helper methods for variables check
# ToDo return logging on empty provider envs
# ToDo Write methods for each provider with async upload of a file to the bucket
# ToDo Write handler that uploads folder for each provider


class S3:
    """Implements S3 storage related operations."""

    def __init__(self, env_path: str):
        """Initializes class S3 with bucket name."""
        load_dotenv(dotenv_path=env_path)  # FixMe remove in final
        self.s3_bucket = os.getenv('BUCKET')
        self.mongo_dump_key = f'/tmp/mongo-dump-{str(datetime.date.today())}.json'

    def __make_azure_client(self):
        """Creates Azure client with provided credentials.

        Returns:
            False: if no connection string provided
            azure_s3: bucket object that will be used to operate with Azure API
        """
        azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if azure_connection_string is not None and azure_connection_string != '':
            logging.info('Azure connection parameters found.')
            azure_connection = BlobServiceClient.from_connection_string(azure_connection_string)
            azure_s3 = azure_connection.get_container_client(self.s3_bucket)
            try:
                azure_s3.create_container()
            except ResourceExistsError:
                logging.info('Container "%s" already exists.', self.s3_bucket)
            return azure_s3
        return False

    def __make_aws_client(self):
        """Creates AWS boto3 client with provided credentials.

        Returns:
            False: if no connection string provided
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
                aws_s3 = boto3.client('s3', region_name=aws_region)
                location = {'LocationConstraint': aws_region}
                try:
                    aws_s3.create_bucket(Bucket=self.s3_bucket, CreateBucketConfiguration=location)
                    return aws_s3
                except AmazonClientError as exc:
                    if exc.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                        logging.info('Container "%s" already exists.', self.s3_bucket)
                        return aws_s3
                    else:
                        logging.error(exc)
        return False

    def __make_gcp_client(self):
        """Creates GCP client with provided credentials.

        Returns:
            False: if no connection string provided
            gcp_s3: bucket object that will be used to operate with GCP API
        """
        google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not env_exists(google_application_credentials) or not Path(google_application_credentials).is_file():
            if not self.generate_gcp_key():
                return False
        logging.info('GCP connection parameters found.')
        gcp_s3 = storage.Client()
        try:
            gcp_s3.create_bucket(self.s3_bucket)
            return gcp_s3
        except GoogleClientError as e:
            if 'You already own this bucket' in str(e):
                logging.info('Container "%s" already exists.', self.s3_bucket)
                return gcp_s3
            logging.error(e)
        return False

    def generate_gcp_key(self):
        service_type = os.getenv('TYPE')
        project_id = os.getenv('PROJECT_ID')
        private_key_id = os.getenv('PRIVATE_KEY_ID')
        private_key = os.getenv('PRIVATE_KEY')
        client_email = os.getenv('CLIENT_EMAIL')
        client_id = os.getenv('CLIENT_ID')
        auth_uri = os.getenv('AUTH_URI')
        token_uri = os.getenv('TOKEN_URI')
        auth_provider_x509_cert_url = os.getenv('AUTH_PROVIDER_X509_CERT_URL')
        client_x509_cert_url = os.getenv('CLIENT_X509_CERT_URL')

        if env_exists(service_type) and env_exists(project_id) and env_exists(private_key_id) \
                and env_exists(private_key) and env_exists(client_email) and env_exists(client_id) \
                and env_exists(auth_uri) and env_exists(token_uri) and env_exists(auth_provider_x509_cert_url) \
                and env_exists(client_x509_cert_url):

            gcp_key_dict = {
                "type": service_type,
                "project_id": project_id,
                "private_key_id": private_key_id,
                "private_key": private_key,
                "client_email": client_email,
                "client_id": client_id,
                "auth_uri": auth_uri,
                "token_uri": token_uri,
                "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
                "client_x509_cert_url": client_x509_cert_url
            }

            with open(self.mongo_dump_key, 'w') as gcp_key_file:
                json.dump(gcp_key_dict, gcp_key_file, indent=2)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.mongo_dump_key
            return True
        return False

    def create_storage_clients(self):
        """Creates client connections from env for the cloud to be used."""
        providers = dict()
        azure_s3 = self.__make_azure_client()
        aws_s3 = self.__make_aws_client()
        gcp_s3 = self.__make_gcp_client()
        if azure_s3:
            providers['azure'] = azure_s3
        if aws_s3:
            providers['aws'] = aws_s3
        if gcp_s3:
            providers['gcp'] = gcp_s3
        logging.info(providers)  # FixMe set to debug or remove
        return providers


if __name__ == '__main__':
    env = Path('/home/exesse/Bin/python/mongo-dump/dev.env')
    cloud = S3(env)
    cloud.create_storage_clients()

