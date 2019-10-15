#!/bin/sh
cd $WORKDIR

gunicorn bothub_nlp_api.wsgi --timeout 999999 -c gunicorn.conf.py
