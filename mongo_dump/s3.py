"""Module contains cloud S3 storage related methods."""


import os
import json
import logging
import datetime
from pathlib import Path
from boto3 import client as aws_client
from google.cloud import storage as gcp_client
from azure.storage.blob import BlobServiceClient as AzureClient
from botocore.exceptions import ClientError as AmazonClientError
from google.cloud.exceptions import ClientError as GoogleClientError
from azure.core.exceptions import AzureError
from azure.core.exceptions import ResourceExistsError as AzureResourceExistsError
from .helpers import env_exists, log


log()

# ToDo Write methods for each provider with sync upload of a file to the bucket
# ToDo Write handler that uploads folder for each provider


class S3:
    """Implements S3 storage related operations."""

    def __init__(self):
        """Initializes class S3 with bucket name."""
        self.s3_bucket = os.getenv('BUCKET')
        self.mongo_dump_key = f'/tmp/mongo-dump-{str(datetime.date.today())}.json'

    def __make_azure_client(self):
        """Creates Azure client with provided credentials.

        Returns:
            False: if no connection string provided
            azure_s3: bucket object that will be used to operate with Azure API
        """
        azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if env_exists(azure_connection_string):
            logging.info('Azure connection parameters found.')
            azure_connection = AzureClient.from_connection_string(azure_connection_string)
            azure_s3 = azure_connection.get_container_client(self.s3_bucket)
            try:
                azure_s3.create_container()
                return azure_s3
            except AzureResourceExistsError:
                logging.info('Container "%s" already exists on Azure and owned by you.', self.s3_bucket)
                return azure_s3
            except AzureError as error_response:
                logging.error(error_response)
        return False

    def __make_aws_client(self):
        """Creates AWS boto3 client with provided credentials.

        Returns:
            False: if no connection string provided
            aws_s3: bucket object that will be used to operate with Amazon API
        """
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION')
        if env_exists(aws_access_key_id) and env_exists(aws_secret_access_key):
            logging.info('AWS connection parameters found.')
            if not env_exists(aws_region):
                aws_region = 'us-west-2'
            logging.info('"%s" will be used as AWS region', aws_region)
            aws_s3 = aws_client('s3', region_name=aws_region)
            location = {'LocationConstraint': aws_region}
            try:
                aws_s3.create_bucket(Bucket=self.s3_bucket, CreateBucketConfiguration=location)
                return aws_s3
            except AmazonClientError as error_response:
                if error_response.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                    logging.info('Container "%s" already exists on AWS and owned by you.', self.s3_bucket)
                    return aws_s3
                else:
                    logging.error(error_response)
        return False

    def __make_gcp_client(self):
        """Creates GCP client with provided credentials.

        Returns:
            False: if no connection string provided
            gcp_s3: bucket object that will be used to operate with GCP API
        """
        google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        google_region = os.getenv('GOOGLE_REGION')
        if not env_exists(google_application_credentials) or not Path(google_application_credentials).is_file():
            if not self.__generate_gcp_key():
                return False
        logging.info('GCP connection parameters found.')
        gcp_s3 = gcp_client.Client()
        for existing_bucket in gcp_s3.list_buckets():
            if existing_bucket.name == self.s3_bucket:
                logging.info('Container "%s" already exists on GCP and owned by you.', self.s3_bucket)
                return gcp_s3
        if not env_exists(google_region):
            google_region = 'us'
        try:
            logging.info('"%s" will be used as AWS region', google_region)
            gcp_s3.create_bucket(self.s3_bucket, location=google_region)
            return gcp_s3
        except GoogleClientError as error_response:
            logging.error(error_response)
        return False

    def __generate_gcp_key(self) -> bool:
        """Inspects environmental variables and generates temporary GCP key

        Returns:
            False: if some of the required parameters are missing
            True: if the key was successfully generated
        """
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

    def __remove_gcp_key(self):
        """Removes temporary GCP access key

        Returns:
            False: if some error occurred
            True: if the key was removed
        """
        if Path(self.mongo_dump_key).is_file():
            try:
                os.remove(self.mongo_dump_key)
            except os.error as exc:
                logging.error(exc)
                return False
        return True

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
        self.__remove_gcp_key()  # FixMe remove later
        return providers
