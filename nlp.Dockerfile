FROM ubuntu:18.04 as base

ENV WORKDIR /home/root/app
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHON_WHEELS_PATH /wheels
ENV PYTHON_BUILD_PACKAGES "software-properties-common curl"
ENV PIP_REQUIREMENTS "-r requirements.txt"

WORKDIR ${WORKDIR}

RUN apt-get update && apt-get install --no-install-recommends -y ${PYTHON_BUILD_PACKAGES} git
RUN apt-get install -y python3 python3-pip python3-venv
RUN apt-get install build-essential

RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
RUN apt-get install -y ttf-mscorefonts-installer \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*


RUN bash -c "ln -s /usr/bin/python3 /usr/bin/python; ln -s /usr/bin/pip3 /usr/bin/pip"

COPY requirements.txt .

FROM base as builder

ENV BUILD_PACKAGES "build-essential"

RUN apt-get update && apt-get install --no-install-recommends -y ${BUILD_PACKAGES}

RUN pip install --upgrade pip

RUN pip install -U pip setuptools

RUN pip wheel --wheel-dir=${PYTHON_WHEELS_PATH} ${PIP_REQUIREMENTS}

FROM base

COPY --from=builder ${PYTHON_WHEELS_PATH} ${PYTHON_WHEELS_PATH}

RUN pip install --upgrade pip

RUN pip install -U pip setuptools

RUN pip install --find-links=${PYTHON_WHEELS_PATH} ${PIP_REQUIREMENTS}

COPY bothub ${WORKDIR}/bothub

COPY start_celery.py .
COPY celery_app.py .

ARG DOWNLOAD_MODELS
#Install torch with cuda 10.1
RUN if [ "${DOWNLOAD_MODELS}" = "pt_br-BERT" ]; then \
        pip install torch==1.6.0+cu101 torchvision==0.7.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html; \
    fi

RUN if [ ${DOWNLOAD_MODELS} ]; then \
        python3.6 bothub/shared/utils/scripts/download_models.py ${DOWNLOAD_MODELS}; \
    fi

ENTRYPOINT [  "celery", "worker", "--autoscale", "1,1", "-O", "fair", "--workdir", ".", "-A", "celery_app", "-c", "5", "-l", "INFO", "-E", "--pool", "threads" ]
