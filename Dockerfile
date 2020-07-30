FROM ubuntu:20.10

RUN groupadd -g 2000 scm
RUN useradd -d /home/scm -u 1000 -g 2000 scm

RUN mkdir /home/scm && mkdir /home/scm/.kube

COPY *.py /home/scm
COPY templates /home/scm/templates
COPY config /home/scm/.kube
COPY requirements.txt /home/scm

RUN chown -R scm:scm /home/scm

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

RUN pip3 install -r /home/scm/requirements.txt

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
    mv kubectl /usr/bin &&\
    chmod 777 /usr/bin/kubectl

USER scm
WORKDIR /home/scm

ENTRYPOINT python3 api.py
