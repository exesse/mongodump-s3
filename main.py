#!/bin/env python3
"""mongo-dump is a S3 storage compatible backup utility for MongoDB."""

from mongodump_s3 import MongoDumpS3

main = MongoDumpS3

if __name__ == '__main__':
    main()
