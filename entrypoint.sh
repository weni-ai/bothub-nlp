#!/bin/bash
WEBAPP_HOME=/home/bothub/app
PYTHON_VENV=/home/bothub/env
PYTHON=$PYTHON_VENV/bin/python
git clone $APP_REPOSITORY_URL bothub
if [ -n "$APP_CHECKOUT_SHA1" ]; then
    cd app
    git checkout $APP_CHECKOUT_SHA1
    cd -
fi

# Configure timezone
if [ "$CONTAINER_TIMEZONE" ]; then
    echo ${CONTAINER_TIMEZONE} >/etc/timezone && \
    ln -sf /usr/share/zoneinfo/${CONTAINER_TIMEZONE} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata
fi

source $PYTHON_VENV/bin/activate
pip install -r $WEBAPP_HOME/requirements.txt
supervisord -n