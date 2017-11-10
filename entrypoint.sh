#!/bin/bash
WEBAPP_HOME=/home/app/webapp
PYTHON_VENV=/home/app/webapp/env
PYTHON=$PYTHON_VENV/bin/python
git clone $APP_REPOSITORY_URL bothub
cd bothub
git checkout $APP_REPOSITORY_BRANCH
chmod +x app/server.py
chmod +x ../supervisor_command.sh

# Configure timezone
if [ "$CONTAINER_TIMEZONE" ]; then
    echo ${CONTAINER_TIMEZONE} >/etc/timezone && \
    ln -sf /usr/share/zoneinfo/${CONTAINER_TIMEZONE} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata
fi

source $PYTHON_VENV/bin/activate
python -m spacy download en
supervisord -n