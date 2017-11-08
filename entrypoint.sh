#!/bin/bash
WEBAPP_HOME=/home/app/webapp
PYTHON_VENV=/home/app/webapp/env
PYTHON=$PYTHON_VENV/bin/python
LC_ALL=C.UTF-8
LANG=C.UTF-8
git clone $APP_REPOSITORY_URL bothub
cd bothub
git checkout $APP_REPOSITORY_BRANCH
chmod +x app/server.py

# Configure timezone
if [ "$CONTAINER_TIMEZONE" ]; then
    echo ${CONTAINER_TIMEZONE} >/etc/timezone && \
    ln -sf /usr/share/zoneinfo/${CONTAINER_TIMEZONE} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata
fi

source $PYTHON_VENV/bin/activate
echo $WEBAPP_HOME/bothub/requirements.txt
pip install -r $WEBAPP_HOME/bothub/requirements.txt
python -m spacy download en
supervisord -n