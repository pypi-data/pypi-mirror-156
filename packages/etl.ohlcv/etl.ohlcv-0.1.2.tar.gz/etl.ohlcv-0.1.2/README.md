![OHLCV ETL Service](external/images/etl-ohlcv.png)

![Python](https://img.shields.io/badge/Python-3.7%20|%203.8%20|%203.9%20|%203.10-blue)
![Product](https://img.shields.io/badge/Product-etl-green)
![Service](https://img.shields.io/badge/Service-ohlcv-green)

## Release procedures

### Preamble

Before attempting to do an update release, you must first:

1. be an Administrator user in the Quant Dev's AWS Account
2. have the latest version of AWS CLI installed
3. have the latest version of Docker installed

You need to configure your AWS CLI and login to Amazon ECR as well:

```shell
$ aws configure
$ aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 766332081706.dkr.ecr.us-east-2.amazonaws.com
```

### Release commands

```shell
$ docker build -t etl-ohlcv-indexer .
$ docker tag etl-ohlcv-indexer:latest 766332081706.dkr.ecr.us-east-2.amazonaws.com/etl-ohlcv-indexer:latest
$ docker push 766332081706.dkr.ecr.us-east-2.amazonaws.com/etl-ohlcv-indexer:latest
```

After running the commands above, you've only successfully built and pushed the latest version of the Docker image. You now need to trigger an update the the actual service ECS.

```shell
aws ecs update-service --cluster etl --service etl-ohlcv-indexer-service --force-new-deployment --region us-east-2
```

## Contribution guidelines

If you want to contribute to **ETL OHLCV**, be sure to review the [contribution guidelines](CONTRIBUTING.md). By participating, you are expected to uphold this guidelines.
