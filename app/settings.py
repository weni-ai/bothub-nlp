from decouple import config

import redis
import logging


MAX_USAGE_MEMORY = config('MAX_USAGE_MEMORY', default=80, cast=int)
DEBUG = config('BOTHUB_DEBUG', default=False, cast=bool)

# Timer to bot timeout (60 minutes)
BOT_REMOVER_TIME = config('BOT_REMOVER_TIME', default=60, cast=int)

# Interval timer garbage collector 60 seconds
GARBAGE_COLLECTOR_TIMER = config('GARBAGE_COLLECTOR_TIMER', default=60.0, cast=float)

# Timer for redis key SERVER-ALIVE-(IP)
SERVER_ALIVE_TIMER = config('SERVER_ALIVE_TIMER', default=70, cast=int)

AWS_URL_INSTANCES_INFO = 'http://169.254.169.254/latest/meta-data/local-ipv4'

LOCAL_IP = config('LOCAL_IP', default='127.0.0.1')

REDIS_CONNECTION = redis.ConnectionPool(host=config('BOTHUB_REDIS'), port=config('BOTHUB_REDIS_PORT'), db=config('BOTHUB_REDIS_DB'))

READ = 0
EDIT = 1
OWNER = 2

ALL_PERMISSIONS = [READ, EDIT, OWNER]

REPOSITORY_PERMISSIONS = [
    'Read',
    'Edit',
    'Owner'
]

logging.basicConfig(filename="bothub-nlp.log")
logger = logging.getLogger('bothub NLP - Bot Manager')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
