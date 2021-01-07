"""Initializes package mongodump-s3."""

from .s3 import S3
from .dump import MongoDump
from .notifications import Notifications

__version__ = '1.1.0'
__author__ = 'Vladislav I. Kulbatski'
__all__ = ['MongoDump', 'S3', 'Notifications', '__version__']
