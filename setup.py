import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="mongodump-s3",
    version="1.1.0",
    description="Backup utility for MongoDB. "
                "Compatible with Azure, Amazon Web Services and Google Cloud Platform.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/exesse/mongodump-s3",
    author="Vladislav I. Kulbatski ",
    author_email="hi@exesse.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["mongodump_s3"],
    include_package_data=False,
    install_requires=[
        "requests==2.25.1",
        "hurry.filesize==0.9",
        "python-dotenv==0.15.0",
        "azure-storage-blob==12.6.0",
        "boto3==1.16.50",
        "google-cloud-storage==1.35.0"
        ],
    entry_points={
        "console_scripts": [
            "mongodump-s3=mongodump_s3.__main__:main",
        ]
    },
)
