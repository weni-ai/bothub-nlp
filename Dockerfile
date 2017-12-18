FROM ubuntu:16.04

MAINTAINER vctrferreira
ENV BASE_PATH=/home/app/webapp
ENV CONTAINER_TIMEZONE=America/Sao_Paulo
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
WORKDIR ${BASE_PATH}

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git
RUN apt-get install -y python3
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-setuptools
RUN apt-get install -y python3-pip
RUN apt-get install -y tzdata
RUN apt-get install -y supervisor
RUN apt-get install -y libpq-dev
RUN pip3 install -U pip setuptools
RUN pip3 install virtualenv
RUN pip3 install redis
RUN virtualenv -p python3 env
RUN env/bin/pip install psycopg2

COPY requirements.txt ${BASE_PATH}
RUN env/bin/pip install -r requirements.txt

RUN env/bin/python -m spacy download en
RUN env/bin/python -m spacy download de
RUN env/bin/python -m spacy download es
RUN env/bin/python -m spacy download pt
RUN env/bin/python -m spacy download fr
RUN env/bin/python -m spacy download it
RUN env/bin/python -m spacy download nl

# setup all the configfiles
# COPY .ssh/ /root/.ssh
# RUN chmod 400 /root/.ssh/id_rsa*

# Timezone configurations.
RUN echo ${CONTAINER_TIMEZONE} >/etc/timezone
RUN ln -sf /usr/share/zoneinfo/${CONTAINER_TIMEZONE} /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

COPY supervisor_command.sh ${BASE_PATH}
COPY supervisor-app.conf /etc/supervisor/conf.d/
COPY entrypoint.sh ${BASE_PATH}

RUN chmod +x ${BASE_PATH}/entrypoint.sh

ENTRYPOINT ${BASE_PATH}/entrypoint.sh

EXPOSE 80