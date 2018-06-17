#!/bin/sh
gunicorn -k tornado -c gunicorn.conf.py app.server:app
