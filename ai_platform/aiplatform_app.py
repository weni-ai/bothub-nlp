import argparse

from bothub.shared.train import train_update as train
from bothub.shared.evaluate_crossval import (
    evaluate_crossval_update as evaluate_crossval,
)

if __name__ == "__main__":
    from settings import (
        operation,
        repository_version_language,
        by_id,
        repository_authorization,
        aws_bucket_authentication,
        language
    )

    # Run the job
    if operation == "train":
        train(
            repository_version_language,
            by_id,
            repository_authorization,
            from_queue="ai-platform",
        )
    elif operation == "evaluate":
        evaluate_crossval(
            repository_version_language,
            repository_authorization,
            aws_bucket_authentication,
            language
        )
