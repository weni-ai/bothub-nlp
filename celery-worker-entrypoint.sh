#!/bin/bash

celery worker -A bothub_nlp.core.celery -c 1 -l INFO $@
