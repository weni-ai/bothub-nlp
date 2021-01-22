import bothub_backend
import argparse
from decouple import config


def backend():
    PARSER = argparse.ArgumentParser()

    # Input Arguments
    PARSER.add_argument(
        "--base_url", help="Base URL API Engine.", type=str, default=None
    )

    ARGUMENTS, _ = PARSER.parse_known_args()

    return bothub_backend.get_backend(
        "bothub_backend.bothub.BothubBackend",
        ARGUMENTS.base_url
        if ARGUMENTS.base_url
        else config("BOTHUB_ENGINE_URL", default="https://api.bothub.it"),
    )
