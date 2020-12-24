"""Module contains cloud S3 storage related methods."""


import os
import logging

from pathlib import Path
from azure.storage.blob import BlobServiceClient as AzureClient
from azure.core.exceptions import AzureError
from azure.core.exceptions import ResourceExistsError as AzureResourceExistsError
from boto3 import client as aws_client
from botocore.exceptions import ClientError as AmazonClientError
from google.cloud import storage as gcp_client
from google.cloud.exceptions import ClientError as GoogleClientError
from google.auth.exceptions import DefaultCredentialsError as GoogleAuthError

from .helpers import env_exists


# TODO pytype, yapf and pylint
# ToDo Write handler that uploads folder for each provider


class S3:
    """Implements S3 storage related operations."""

    def __init__(self):
        """Initializes class S3 with bucket name."""
        self.s3_bucket = os.getenv('BUCKET')
        self.providers = self.create_storage_clients()  #TODO decide if usage would be efficient

    def _make_azure_client(self):
        """Creates Azure client with provided credentials.

        Returns:
            False: if no connection string provided
            azure_s3: bucket object that will be used to operate with Azure API
        """
        azure_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if env_exists(azure_connection_string):
            logging.info('Azure connection parameters found.')
            azure_s3 = AzureClient.from_connection_string(azure_connection_string)
            try:
                azure_s3.create_container(self.s3_bucket)
                logging.info('Container "%s" successfully created on Azure.', self.s3_bucket)
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
            aws_s3 = aws_client('s3', region_name=aws_region)
            location = {'LocationConstraint': aws_region}
            try:
                aws_s3.create_bucket(Bucket=self.s3_bucket, CreateBucketConfiguration=location)
                logging.info('"%s" was created in region "%s" on AWS', self.s3_bucket, aws_region)
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
                gcp_s3.create_bucket(self.s3_bucket, location=google_region)
                logging.info('"%s" was created in region "%s" on GCP', self.s3_bucket, google_region)
                return gcp_s3
            except GoogleAuthError as error_response:
                logging.error(error_response)
            except GoogleClientError as error_response:
                logging.error(error_response)
        return False

    def create_storage_clients(self):
        """Creates client connections from env for the cloud to be used."""
        providers = {}
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

    def upload_local_file(self, local_file_path: str, *remote_file_path: str) -> bool:
        """Uploads the file to the specified bucket.

        Args:
            local_file_path: str, full path to local file
            remote_file_path: str, optional name for remote file,
                              if not provided will be the same as local_file_path

        Returns:
            False: if folder upload failed, or folder doesn't exists
            True: if folder upload succeeded
        """
        if not remote_file_path:
            remote_file_path = local_file_path
        remote_file_path = str(remote_file_path[0])

        if Path(local_file_path).is_file():
            if 'azure' in self.providers:
                azure_s3 = self.providers['azure']
                try:
                    blob = azure_s3.get_blob_client(container=self.s3_bucket, blob=remote_file_path)
                    with open(local_file_path, "rb") as data:
                        blob.upload_blob(data)
                    logging.info('"%s" was successfully uploaded to the "%s" bucket on Azure.', local_file_path,
                                 self.s3_bucket)
                except AzureError as error_response:
                    exists_error = 'The specified blob already exists.'
                    if exists_error in str(error_response):
                        logging.info('"%s" already exists in the "%s" bucket on Azure.', remote_file_path, self.s3_bucket)
                    else:
                        logging.error(error_response)
            if 'aws' in self.providers:
                aws_s3 = self.providers['aws']
                try:
                    aws_s3.upload_file(local_file_path, self.s3_bucket, remote_file_path)
                    logging.info('"%s" was successfully uploaded to the "%s" bucket on AWS.', local_file_path, self.s3_bucket)
                except AmazonClientError as error_response:
                    logging.error(error_response)
            if 'gcp' in self.providers:
                gcp_s3 = self.providers['gcp']
                try:
                    # TODO set remote filename property
                    gcp_s3_client = gcp_s3.get_bucket(self.s3_bucket)
                    blob = gcp_s3_client.blob(local_file_path)
                    blob.upload_from_filename(local_file_path)
                    logging.info('"%s" was successfully uploaded to the "%s" bucket on GCP.', local_file_path, self.s3_bucket)
                except GoogleClientError as error_response:
                    logging.error(error_response)
            return True
        logging.error('"%s" does not exists', local_file_path)
        return False

    def upload_local_folder(self, local_folder_path: str, remove_path_parent: str = '') -> bool:
        """Uploads local folder to remote S3 storage.

        Args:
            local_folder_path: str, full path to the local folder to be uploaded
            remove_path_parent: str, optional, part that will be subtracted from full file path in the naming of remote file

        Returns:
            False: if folder upload failed, or folder doesn't exists
            True: if folder upload succeeded
        """
        if Path(local_folder_path).is_dir():
            for local_file in Path(local_folder_path).rglob('*'):
                if Path(local_file).is_file():
                    if remove_path_parent == '':
                        remote_file = local_file
                    else:
                        remote_file = local_file.relative_to(remove_path_parent)
                    local_file_name = str(local_file)
                    remote_file_name = str(remote_file)
                    self.upload_local_file(local_file_name, remote_file_name)
            logging.info('"%s" was successfully uploaded to s3 storage', local_folder_path)
            return True
        logging.error('"%s" folder does not exists. Please check.', local_folder_path)
        return False
