import environ
from collections import OrderedDict


def cast_supported_languages(i):
    return OrderedDict([x.split(":", 1) if ":" in x else (x, x) for x in i.split("|")])


environ.Env.read_env(env_file=(environ.Path(__file__) - 2)(".env"))

env = environ.Env(
    # set casting, default value
    BOTHUB_NLP_API_PORT=(int, 2657),
    BOTHUB_NLP_SENTRY_CLIENT=(bool, None),
    SUPPORTED_LANGUAGES=(cast_supported_languages, "en|pt"),
    BOTHUB_ENGINE_URL=(str, "https://api.bothub.it"),
)

BOTHUB_NLP_API_PORT = env.int("BOTHUB_NLP_API_PORT")

BOTHUB_NLP_SENTRY_CLIENT = env.bool("BOTHUB_NLP_SENTRY_CLIENT")

SUPPORTED_LANGUAGES = env.get_value(
    "SUPPORTED_LANGUAGES", cast_supported_languages, "en|pt", True
)

BOTHUB_ENGINE_URL = env.str("BOTHUB_ENGINE_URL")
