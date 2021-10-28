from decouple import config

# Period of time (seconds) the worker will look for idle interpreters to free space
WORKER_CACHE_CLEANING_PERIOD = config(
    "WORKER_CACHE_CLEANING_PERIOD", cast=float, default=3*3600
)
# Idle limit of time (seconds) the interpreter will be cached
INTERPRETER_CACHE_IDLE_LIMIT = config(
    "INTERPRETER_CACHE_IDLE_LIMIT", cast=float, default=24*3600
)
