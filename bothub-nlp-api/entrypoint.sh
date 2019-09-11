#!/bin/sh
cd $WORKDIR

gunicorn bothub_nlp_api.wsgi -c gunicorn.conf.py