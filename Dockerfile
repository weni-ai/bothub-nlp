FROM ubuntu:18.04 as base

ENV WORKDIR /home/root/app
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHON_WHEELS_PATH /wheels
ENV PYTHON_BUILD_PACKAGES "software-properties-common curl"
ENV BUILD_PACKAGES "build-essential"

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

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apt-get update && apt-get install --no-install-recommends -y ${BUILD_PACKAGES}

RUN pip install pipenv

RUN pipenv install --system

FROM base

COPY . .

RUN git clone --branch master --depth 1 --single-branch \
    https://github.com/Ilhasoft/spacy-lang-models \
    spacy-langs \
    && python3.6 scripts/link_lang_spacy.py pt_br ./spacy-langs/pt_br/ \
    && python3.6 scripts/link_lang_spacy.py mn ./spacy-langs/mn/ \
    && python3.6 scripts/link_lang_spacy.py ha ./spacy-langs/ha/ \
    && python3.6 scripts/link_lang_spacy.py ka ./spacy-langs/ka/ \
    && python3.6 scripts/link_lang_spacy.py kk ./spacy-langs/kk/ \
    && python3.6 scripts/link_lang_spacy.py sw ./spacy-langs/sw/

ARG DOWNLOAD_SPACY_MODELS

RUN if [ ${DOWNLOAD_SPACY_MODELS} ]; then \
        python3.6 bothub_nlp_nlu_worker/bothub_nlp_nlu/scripts/download_spacy_models.py ${DOWNLOAD_SPACY_MODELS}; \
    fi

ENTRYPOINT [ "celery", "worker", "-A", "bothub_nlp_nlu_worker.celery_app", "-c", "1", "-l", "INFO", "-E" ]
