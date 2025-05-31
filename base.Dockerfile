FROM ubuntu:24.04

ARG PYTHON_VENV_PATH=/python/venv

ENV DEBIAN_FRONTEND=noninteractive

# Install package dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        software-properties-common \
        autoconf \
        automake \
        libtool \
        pkg-config \
        ca-certificates \
        locales \
        locales-all \
        python3-full \
        git \
        wget && \
    apt-get clean

# install weasyprint & dependencies
RUN apt-get update && \
    apt-get install -y gcc libpq-dev \
        libcairo2 libcairo2-dev libpangocairo-1.0-0 weasyprint && \
    apt-get clean && \
    rm -rf /var/cache/apt/*

# System locale
ENV LC_ALL=en_GB.UTF-8
ENV LANG=en_GB.UTF-8
ENV LANGUAGE=en_GB.UTF-8

RUN mkdir -p ${PYTHON_VENV_PATH} && \
    python3 -m venv ${PYTHON_VENV_PATH}

ENV PATH=${PYTHON_VENV_PATH}/bin:$PATH

RUN cd ${PYTHON_VENV_PATH}/bin && \
    pip install --upgrade pip