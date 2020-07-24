FROM ubuntu:20.10

RUN groupadd -g 2000 scm
RUN useradd -d /SCM -u 1000 -g 2000 scm

RUN mkdir /SCM && mkdir /SCM/.kube

COPY api.py /SCM/api.py
COPY templates /SCM/templates
COPY config /SCM/.kube
COPY requirements.txt /SCM

RUN chown -R scm:scm /SCM

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

RUN pip3 install -r /SCM/requirements.txt

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl && \
    mv kubectl /usr/bin &&\
    chmod 777 /usr/bin/kubectl

USER scm
WORKDIR /SCM

ENTRYPOINT python3 api.py
