from decouple import config

import redis


MAX_USAGE_MEMORY = config('MAX_USAGE_MEMORY', default=80, cast=int)
DEBUG = True

# Timer to bot timeout (60 minutes)
BOT_REMOVER_TIME = config('BOT_REMOVER_TIME', default=60, cast=int)

# Interval timer garbage collector 60 seconds
GARBAGE_COLLECTOR_TIMER = config('GARBAGE_COLLECTOR_TIMER', default=60.0, cast=float)

# Timer for redis key SERVER-ALIVE-(IP)
SERVER_ALIVE_TIMER = config('SERVER_ALIVE_TIMER', default=70, cast=int)

AWS_URL_INSTANCES_INFO = 'http://169.254.169.254/latest/meta-data/local-ipv4'

LOCAL_IP = config('LOCAL_IP', default='127.0.0.1')
