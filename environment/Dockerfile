# hash:sha256:e173fa6ed38e549046620079cfe7ec2ab9811afed0eacf8d8e3df7b91f7a8b24
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/jupyterlab:3.0.9-miniconda4.9.2-python3.8-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN pip install -U --no-cache-dir \
    aind-data-schema \
    aind-data-schema-models \
    aind-log-utils \
    aws-requests-auth \
    boto3 \
    matplotlib \
    numpy \
    pandas
