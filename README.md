## mongo-dump is a S3 storage compatible backup utility for MongoDB.

### Docker

````bash
sudo docker run --name mongo-dump --env-file dev.env -d -v ~/mongo-dump:/tmp/mongo-dump mongo-dump:0.0.1-dev
````

!Temporary 
```bash
docker build -t mongo-dump:0.0.1-dev .

sudo docker stop mongo-dump && sudo docker rm mongo-dump && sudo docker rmi mongo-dump:0.0.1-dev
```