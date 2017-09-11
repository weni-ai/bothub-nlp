#!/bin/bash
WEBAPP_HOME=/home/app/webapp
PYTHON_VENV=/home/app/webapp/env
PYTHON=$PYTHON_VENV/bin/python
git clone $APP_REPOSITORY_URL bothub
cd bothub
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
supervisord -n