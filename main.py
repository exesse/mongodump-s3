#!/bin/env python3
"""mongo-dump is a S3 storage compatible backup utility for MongoDB."""


from mongodump_s3 import MongoDumpS3


# ToDo parse dump result here
# ToDo parse upload result here


def main():
    MongoDumpS3().exec()


if __name__ == '__main__':
    main()
