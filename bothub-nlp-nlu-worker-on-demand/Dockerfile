FROM ubuntu:xenial

ENV WORKDIR /root/app
ENV BOTHUB_NLP_WORKER_ON_DEMAND_API_PORT 2658
ENV PYTHON_BUILD_PACKAGES "software-properties-common curl"

WORKDIR $WORKDIR

COPY bothub-nlp-nlu-worker-on-demand .

RUN apt-get update \
    && apt-get install --no-install-recommends -y ${PYTHON_BUILD_PACKAGES} git locales \
    && add-apt-repository ppa:fkrull/deadsnakes \
    && apt-get update \
    && apt-get install --no-install-recommends -y python3.6 python3.6-dev python3.6-tk build-essential \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.6 get-pip.py \
    && rm get-pip.py

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pip install pipenv redis
RUN pipenv install --system --deploy
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "python", "-m", "bothub_nlp_nlu_worker_on_demand" ]
