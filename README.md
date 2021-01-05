# mongo-dump
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0484d1d38b5d41318f0980126a1c45a9)](https://www.codacy.com/gh/exesse/mongodump-s3/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=exesse/mongodump-s3&amp;utm_campaign=Badge_Grade)
[![DeepSource](https://deepsource.io/gh/exesse/mongodump-s3.svg/?label=active+issues&show_trend=true)](https://deepsource.io/gh/exesse/mongodump-s3/?ref=repository-badge)
[![release Actions Status](https://github.com/exesse/mongodump-s3/workflows/release/badge.svg)](https://github.com/exesse/mongodump-s3/actions)
[![build Actions Status](https://github.com/exesse/mongodump-s3/workflows/build/badge.svg)](https://github.com/exesse/mongodump-s3/actions)
[![PyPI Version](https://img.shields.io/pypi/v/mongodump-s3)](https://pypi.org/project/mongodump-s3/)
[![Docker Image Size](https://img.shields.io/docker/image-size/exesse/mongodump-s3)](https://hub.docker.com/repository/docker/exesse/mongodump-s3)
 
Backup utility for MongoDB. Compatible with Azure, Amazon Web Services and Google Cloud Platform.

## Installation
Make sure that original MongoDB Database Tools are installed. Please follow instruction on [the official page](https://www.mongodb.com/try/download/database-tools) for platform specific installation.
Also make sure that `mongodump` command is in your PATH.
````bash
pip install mongodump-s3
````

## Usage
`mongodump-s3` could be used as command line tool or as Docker service. There are also three possible ways to pass parameters to the utility:
-   Through setting environment variables
-   By passing env file to the tool
-   Or by passing individual flags

Please refer to `sample.env` [example](https://github.com/exesse/mongodump-s3/blob/main/sample.env) for all possible env options.

### Command line
```bash
$ mongodump-s3 --help
usage: mongodump-s3 <options>

Export the content of a running server into .bson files and uploads to provided S3 compatible storage. By default loads required settings from environment variables.

general options:
  -h, --help            print usage
  -v, --version         print the tool version and exit

output options:
  -b <S3 Bucket>, --bucket <S3 Bucket>
                        S3 bucket name for upload, defaults to 'mongodump'
  -o <folder>, --out <folder>
                        output directory, defaults to 'dump'

uri options:
  -u <uri>, --uri <uri>
                        mongodb uri connection string. See official description here https://docs.mongodb.com/manual/reference/connection-string

environmental options:
  -e <env-file>, --env <env-file>
                        path to file containing environmental variables

cloud storage options:
  --azure "<azure_storage_connection_string>"
                        connection string for storage account provided by Azure
  --aws "<aws_access_key_id=value> <aws_secret_access_key=value> <aws_region=value>"
                        AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION properties provided by Amazon Web Services IAM. AWS_REGION defaults to 'us-west-2' if not specified
  --gcp "<google_application_credentials=value> <google_region=value>"
                        path to service account file and optional Google Cloud Region. GOOGLE_REGION defaults to 'us-multiregion' if not specified

notification options:
  --email <user@example.com>
                        email address which to notify upon the result
  --smtp <mail-server.example.com>
                        SMTP relay server to use, defaults to 'localhost'
  --telegram "<telegram_token=value> <telegram_chat_id=value>"
                        Telegram API token and chat id to be used for notification. See more: https://core.telegram.org/bots/api
```

### Docker
````bash
sudo docker run --name mongo-dump [Optional: --env-file sample.env] exesse/mongo-dump:latest [Optional: startup flags]
````

In case you need to pass GCP service account key please mount the key inside container and simply specify `GOOGLE_APPLICATION_CREDENTIALS=/mongo-dump/key.json`.
```bash
sudo docker run --name mongo-dump-gcp \
    --env-file sample.env \
    -v ~/dev.json:/mongo-dump/key.json:ro \
    exesse/mongo-dump:latest 
```

## Feedback
Email bug reports, questions, discussions to [hi@exesse.org](mailto:hi@exesse.org).