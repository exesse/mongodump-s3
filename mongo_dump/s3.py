"""Module contains cloud S3 storage related methods."""


import os
import logging

from pathlib import Path
from azure.storage.blob import BlobServiceClient as AzureClient
from boto3 import client as aws_client
from google.cloud import storage as gcp_client

from azure.core.exceptions import AzureError
from azure.core.exceptions import ResourceExistsError as AzureResourceExistsError
from botocore.exceptions import ClientError as AmazonClientError
from google.cloud.exceptions import ClientError as GoogleClientError
from google.auth.exceptions import DefaultCredentialsError as GoogleAuthError

from .helpers import env_exists


# ToDo Write methods for each provider with sync upload of a file to the bucket
# ToDo Write handler that uploads folder for each provider


class S3:
    """Implements S3 storage related operations."""

    def __init__(self):
        """Initializes class S3 with bucket name."""
        self.s3_bucket = os.getenv('BUCKET')

    def _make_azure_client(self):
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

    def _make_aws_client(self):
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
                logging.error(error_response)
        return False

    def _make_gcp_client(self):
        """Creates GCP client with provided credentials.

        Returns:
            False: if no connection string provided
            gcp_s3: bucket object that will be used to operate with GCP API
        """
        google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        google_region = os.getenv('GOOGLE_REGION')

        if env_exists(google_application_credentials) and Path(google_application_credentials).is_file():
            logging.info('GCP connection parameters found.')
            if not env_exists(google_region):
                google_region = 'us'
            try:
                gcp_s3 = gcp_client.Client()
                for existing_bucket in gcp_s3.list_buckets():
                    if existing_bucket.name == self.s3_bucket:
                        logging.info('Container "%s" already exists on GCP and owned by you.', self.s3_bucket)
                        return gcp_s3
                logging.info('"%s" will be used as AWS region', google_region)
                gcp_s3.create_bucket(self.s3_bucket, location=google_region)
                return gcp_s3
            except GoogleAuthError as error_response:
                logging.error(error_response)
            except GoogleClientError as error_response:
                logging.error(error_response)
        return False

    def create_storage_clients(self):
        """Creates client connections from env for the cloud to be used."""
        providers = dict()
        azure_s3 = self._make_azure_client()
        aws_s3 = self._make_aws_client()
        gcp_s3 = self._make_gcp_client()
        if azure_s3:
            providers['azure'] = azure_s3
        if aws_s3:
            providers['aws'] = aws_s3
        if gcp_s3:
            providers['gcp'] = gcp_s3
        logging.info(providers)  # FixMe set to debug or remove
        return providers
