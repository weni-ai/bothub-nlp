import argparse

from bothub.shared.train import train_update as train
from bothub.shared.evaluate_crossval import (
    evaluate_crossval_update as evaluate_crossval,
)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()

    # Input Arguments
    PARSER.add_argument(
        "--operation", help='What operation will be done, "train" or "evaluate"'
    )
    PARSER.add_argument(
        "--repository-version", help="The version of repository.", type=int
    )
    PARSER.add_argument("--by-id", help=".", type=int)
    PARSER.add_argument(
        "--repository-authorization", help="Repository authorization string."
    )

    ARGUMENTS, _ = PARSER.parse_known_args()

    # Run the job
    if ARGUMENTS.operation == "train":
        train(
            ARGUMENTS.repository_version,
            ARGUMENTS.by_id,
            ARGUMENTS.repository_authorization,
            from_queue="ai-platform",
        )
    elif ARGUMENTS.operation == "evaluate":
        evaluate_crossval(
            ARGUMENTS.repository_version,
            ARGUMENTS.by_id,
            ARGUMENTS.repository_authorization,
            from_queue="ai-platform",
        )
