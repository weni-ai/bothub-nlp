import argparse

PARSER = argparse.ArgumentParser()

# Input Arguments
PARSER.add_argument(
    "--operation", help='What operation will be done, "train" or "evaluate"'
)
PARSER.add_argument(
    "--repository-version", help="The id of repository-version.", type=int
)
PARSER.add_argument(
    "--by-id", help="User id sending the job", type=int
)
PARSER.add_argument(
    "--repository-authorization", help="Repository authorization string."
)
PARSER.add_argument(
    "--AIPLATFORM_LANGUAGE_QUEUE", type=str, default=""
)

PARSER.add_argument(
    "--BOTHUB_NLP_AWS_S3_BUCKET_NAME", type=str, default=""
)

PARSER.add_argument(
    "--BOTHUB_NLP_AWS_ACCESS_KEY_ID", type=str, default=""
)

PARSER.add_argument(
    "--BOTHUB_NLP_AWS_SECRET_ACCESS_KEY", type=str, default=""
)

PARSER.add_argument(
    "--BOTHUB_NLP_AWS_REGION_NAME", type=str, default="us-east-1"
)

ARGUMENTS, _ = PARSER.parse_known_args()

operation = ARGUMENTS.operation
repository_version_language = ARGUMENTS.repository_version
by_id = ARGUMENTS.by_id
repository_authorization = ARGUMENTS.repository_authorization
language = ARGUMENTS.AIPLATFORM_LANGUAGE_QUEUE

aws_bucket_authentication = {
    "BOTHUB_NLP_AWS_S3_BUCKET_NAME": ARGUMENTS.BOTHUB_NLP_AWS_S3_BUCKET_NAME,
    "BOTHUB_NLP_AWS_ACCESS_KEY_ID": ARGUMENTS.BOTHUB_NLP_AWS_ACCESS_KEY_ID,
    "BOTHUB_NLP_AWS_SECRET_ACCESS_KEY": ARGUMENTS.BOTHUB_NLP_AWS_SECRET_ACCESS_KEY,
    "BOTHUB_NLP_AWS_REGION_NAME": ARGUMENTS.BOTHUB_NLP_AWS_REGION_NAME,
}
