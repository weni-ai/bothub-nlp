FROM ubuntu:xenial as base

ENV WORKDIR /home/root/app
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHON_WHEELS_PATH /wheels
ENV PYTHON_BUILD_PACKAGES "software-properties-common curl"
ENV PIP_REQUIREMENTS "-r requirements.txt"

WORKDIR ${WORKDIR}

RUN apt-get update \
    && apt-get install --no-install-recommends -y ${PYTHON_BUILD_PACKAGES} git \
    && add-apt-repository ppa:fkrull/deadsnakes \
    && apt-get update \
    && apt-get install --no-install-recommends -y python3.6 python3.6-dev python3.6-tk \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.6 get-pip.py \
    && rm get-pip.py \
    && apt-get remove -y ${PYTHON_BUILD_PACKAGES}

RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
RUN apt-get install -y ttf-mscorefonts-installer \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY bothub-nlp-nlu-worker/requirements.txt .

FROM base as builder

ENV BUILD_PACKAGES "build-essential"

RUN apt-get update && apt-get install --no-install-recommends -y ${BUILD_PACKAGES}

RUN pip wheel --wheel-dir=${PYTHON_WHEELS_PATH} ${PIP_REQUIREMENTS}

FROM base

COPY --from=builder ${PYTHON_WHEELS_PATH} ${PYTHON_WHEELS_PATH}

RUN pip install --no-index --find-links=${PYTHON_WHEELS_PATH} ${PIP_REQUIREMENTS}

COPY bothub-nlp-nlu-worker .

RUN git clone --branch master --depth 1 --single-branch \
    https://github.com/Ilhasoft/spacy-lang-models \
    spacy-langs \
    && python3.6 scripts/link_lang_spacy.py pt_br ./spacy-langs/pt_br/ \
    && python3.6 scripts/link_lang_spacy.py mn ./spacy-langs/mn/

ARG DOWNLOAD_SPACY_MODELS

RUN if [ ${DOWNLOAD_SPACY_MODELS} ]; then \
        python3.6 bothub_nlp_nlu_worker/bothub_nlp_nlu/scripts/download_spacy_models.py ${DOWNLOAD_SPACY_MODELS}; \
    fi

ENTRYPOINT [ "celery", "worker", "--workdir", "bothub_nlp_nlu_worker", "-A", "celery_app", "-c", "1", "-l", "INFO", "-E" ]
