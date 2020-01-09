#!/bin/sh
cd $WORKDIR

#gunicorn bothub_nlp_api.wsgi --log-level debug --timeout 999999 -c gunicorn.conf.py
gunicorn -k uvicorn.workers.UvicornWorker --timeout 999999 -c "gunicorn.conf.py" "bothub_nlp_api.app:app"
