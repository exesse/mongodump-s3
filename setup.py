import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="mongodump-s3",
    version="1.0.0",
    description="Read the latest Real Python tutorials",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/exesse/mongodump-s3",
    author="Real Python",
    author_email="hi@exesse.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["mongodump-s3"],
    include_package_data=False,
    install_requires=[
        "requests==2.25.1",
        "hurry.filesize==0.9",
        "python-dotenv==0.15.0",
        "azure-storage-blob==12.6.0",
        "boto3==1.16.48",
        "google-cloud-storage==1.35.0"
        ],
    entry_points={
        "console_scripts": [
            "realpython=mongodump-s3.__main__:main",
        ]
    },
)
