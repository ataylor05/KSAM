FROM ubuntu:20.04

ENV AZURE_CLIENT_ID=#{Az-Client-Id}#
ENV AZURE_CLIENT_SECRET=#{Az-Client-Secret}#
ENV AZURE_TENANT_ID=#{Az-Tenant-Id}#

RUN mkdir /home/ksam \
    && mkdir /home/ksam/.kube \
    && groupadd -g 1000 ksam \
    && useradd -d /home/ksam -u 1000 -g 1000 ksam

COPY kubeconfig /home/ksam/.kube/config
COPY src/*.py /home/ksam/
COPY templates /home/ksam/

RUN chown -R ksam:ksam /home/ksam

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    tar \
    vim \
    wget

RUN pip3 install flask kubernetes pyyaml azure-keyvault

USER ksam
WORKDIR /home/ksam

ENTRYPOINT python3 main.py