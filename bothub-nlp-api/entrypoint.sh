#!/bin/sh
cd $WORKDIR

#gunicorn bothub_nlp_api.wsgi --log-level debug --timeout 999999 -c gunicorn.conf.py
python app.py
