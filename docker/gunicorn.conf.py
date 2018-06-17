import os
# import multiprocessing

current_path = os.path.dirname(os.path.abspath(__file__))
bind = '0.0.0.0:8080'
workers = 1 # multiprocessing.cpu_count() * 2
name = 'bothub-nlp'
proc_name = 'bothub-nlp'
default_proc_name = proc_name
chdir = current_path
loglevel = 'info'
timeout = 240
