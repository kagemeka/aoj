FROM python:3.10.2-slim-buster
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root/
RUN \
    apt update \
    && apt install -y \
    apt-utils \
    curl \
    git \
    make \
    wget \
    fonts-noto-cjk \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
    && echo 'source $HOME/.poetry/env' >> ~/.bashrc \
    && python3 -m pip install -U pip \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb
