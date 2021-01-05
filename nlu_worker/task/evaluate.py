import json
import logging
import uuid

from rasa.nlu import __version__ as rasa_version
from rasa.nlu.test import get_entity_extractors, plot_attribute_confidences
from rasa.nlu.test import get_evaluation_metrics
from rasa.nlu.test import (
    merge_labels,
    _targets_predictions_from,
    remove_empty_intent_examples,
    get_eval_data,
    align_all_entity_predictions,
)
from rasa.nlu.test import plot_confusion_matrix
from rasa.nlu.test import substitute_labels
from rasa.nlu.training_data import Message
from rasa.nlu.training_data import TrainingData

from .utils import backend
from .utils import update_interpreters

logger = logging.getLogger(__name__)

excluded_itens = [
    "micro avg",
    "macro avg",
    "weighted avg",
    "no_entity",
    "no predicted",
    "accuracy",
]


def collect_incorrect_entity_predictions(
    entity_results, merged_predictions, merged_targets
):
    errors = []
    offset = 0
    for entity_result in entity_results:
        for i in range(offset, offset + len(entity_result.tokens)):
            if merged_targets[i] != merged_predictions[i]:
                errors.append(
                    {
                        "text": entity_result.message,
                        "entities": entity_result.entity_targets,
                        "predicted_entities": entity_result.entity_predictions,
                        "entity_status": "error",
                    }
                )
                break
        offset += len(entity_result.tokens)
    return errors


def is_start_end_in_list(entity, predicted_entities):
    for predicted_entity in predicted_entities:
        if (
            entity.get("start") == predicted_entity.get("start")
            and entity.get("end") == predicted_entity.get("end")
            and entity.get("value") == predicted_entity.get("value")
        ):
            return predicted_entity
    return False


def is_entity_in_predicted(entity, predicted_entities, return_predicted=False):
    for predicted_entity in predicted_entities:
        if (
            entity.get("start") == predicted_entity.get("start")
            and entity.get("end") == predicted_entity.get("end")
            and entity.get("value") == predicted_entity.get("value")
            and entity.get("entity") == predicted_entity.get("entity")
        ):
            if return_predicted:
                return predicted_entity, True
            return True
    if return_predicted:
        return None, False
    return False


def is_false_success(sentence_eval):
    for true_entity in sentence_eval["entities"]:
        match = False
        if is_entity_in_predicted(true_entity, sentence_eval["predicted_entities"]):
            match = True
        if match is False:
            return True
    return False


def collect_successful_entity_predictions(
    entity_results, merged_predictions, merged_targets
):
    successes = []
    offset = 0
    for entity_result in entity_results:
        for i in range(offset, offset + len(entity_result.tokens)):
            if (
                merged_targets[i] == merged_predictions[i]
                and merged_targets[i] != "no_entity"
            ):
                successes.append(
                    {
                        "text": entity_result.message,
                        "entities": entity_result.entity_targets,
                        "predicted_entities": entity_result.entity_predictions,
                        "entity_status": "success",
                    }
                )
                break
        offset += len(entity_result.tokens)
    successes = [
        sentence_eval
        for sentence_eval in successes
        if not is_false_success(sentence_eval)
    ]
    return successes


def evaluate_entities(entity_results, extractors):  # pragma: no cover
    """Creates summary statistics for each entity extractor.
    Logs precision, recall, and F1 per entity type for each extractor."""

    aligned_predictions = align_all_entity_predictions(entity_results, extractors)
    merged_targets = merge_labels(aligned_predictions)
    merged_targets = substitute_labels(merged_targets, "O", "no_entity")

    result = {}

    for extractor in extractors:
        merged_predictions = merge_labels(aligned_predictions, extractor)
        merged_predictions = substitute_labels(merged_predictions, "O", "no_entity")

        report, precision, f1, accuracy = get_evaluation_metrics(
            merged_targets,
            merged_predictions,
            output_dict=True,
            exclude_label="no_entity",
        )

        log = collect_incorrect_entity_predictions(
            entity_results, merged_predictions, merged_targets
        ) + collect_successful_entity_predictions(
            entity_results, merged_predictions, merged_targets
        )

        result = {
            "report": report,
            "precision": precision,
            "f1_score": f1,
            "accuracy": accuracy,
            "log": log,
        }

    return result


def collect_nlu_successes(intent_results):
    successes = [
        {
            "text": r.message,
            "intent": r.intent_target,
            "intent_prediction": {
                "name": r.intent_prediction,
                "confidence": r.confidence,
            },
            "intent_status": "success",
        }
        for r in intent_results
        if r.intent_target == r.intent_prediction
    ]
    return successes


def collect_nlu_errors(intent_results):
    errors = [
        {
            "text": r.message,
            "intent": r.intent_target,
            "intent_prediction": {
                "name": r.intent_prediction,
                "confidence": r.confidence,
            },
            "intent_status": "error",
        }
        for r in intent_results
        if r.intent_target != r.intent_prediction
    ]
    return errors


def evaluate_intents(intent_results):  # pragma: no cover
    """Creates a confusion matrix and summary statistics for intent predictions.

    Log samples which could not be classified correctly and save them to file.
    Creates a confidence histogram which is saved to file.
    Wrong and correct prediction confidences will be
    plotted in separate bars of the same histogram plot.
    Only considers those examples with a set intent.
    Others are filtered out. Returns a dictionary of containing the
    evaluation result.
    """

    # remove empty intent targets
    intent_results = remove_empty_intent_examples(intent_results)

    target_intents, predicted_intents = _targets_predictions_from(
        intent_results, "intent_target", "intent_prediction"
    )

    report, precision, f1, accuracy = get_evaluation_metrics(
        target_intents, predicted_intents, output_dict=True
    )

    log = collect_nlu_errors(intent_results) + collect_nlu_successes(intent_results)

    predictions = [
        {
            "text": res.message,
            "intent": res.intent_target,
            "predicted": res.intent_prediction,
            "confidence": res.confidence,
        }
        for res in intent_results
    ]

    return {
        "predictions": predictions,
        "report": report,
        "precision": precision,
        "f1_score": f1,
        "accuracy": accuracy,
        "log": log,
    }


def plot_and_save_charts(update, intent_results):  # pragma: no cover
    import io
    import boto3
    import matplotlib as mpl

    mpl.use("Agg")

    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix
    from sklearn.utils.multiclass import unique_labels
    from botocore.exceptions import ClientError
    from decouple import config

    aws_access_key_id = config("BOTHUB_NLP_AWS_ACCESS_KEY_ID", default="")
    aws_secret_access_key = config("BOTHUB_NLP_AWS_SECRET_ACCESS_KEY", default="")
    aws_bucket_name = config("BOTHUB_NLP_AWS_S3_BUCKET_NAME", default="")
    aws_region_name = config("BOTHUB_NLP_AWS_REGION_NAME", "us-east-1")

    confmat_url = ""
    intent_hist_url = ""

    if all([aws_access_key_id, aws_secret_access_key, aws_bucket_name]):
        confmat_filename = "repository_{}/confmat_{}.png".format(update, uuid.uuid4())
        intent_hist_filename = "repository_{}/intent_hist_{}.png".format(
            update, uuid.uuid4()
        )

        intent_results = remove_empty_intent_examples(intent_results)
        targets, predictions = _targets_predictions_from(
            intent_results, "intent_target", "intent_prediction"
        )

        cnf_matrix = confusion_matrix(targets, predictions)
        labels = unique_labels(targets, predictions)
        plot_confusion_matrix(
            cnf_matrix, classes=labels, title="Intent Confusion matrix"
        )

        chart = io.BytesIO()
        fig = plt.gcf()
        fig.set_size_inches(20, 20)
        fig.savefig(chart, format="png", bbox_inches="tight")
        chart.seek(0)

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name,
        )
        try:
            s3_client.upload_fileobj(
                chart,
                aws_bucket_name,
                confmat_filename,
                ExtraArgs={"ContentType": "image/png"},
            )
            confmat_url = "{}/{}/{}".format(
                s3_client.meta.endpoint_url, aws_bucket_name, confmat_filename
            )
        except ClientError as e:
            logger.error(e)

        plot_attribute_confidences(
            intent_results, None, "intent_target", "intent_prediction"
        )
        chart = io.BytesIO()
        fig = plt.gcf()
        fig.set_size_inches(10, 10)
        fig.savefig(chart, format="png", bbox_inches="tight")
        chart.seek(0)

        try:
            s3_client.upload_fileobj(
                chart,
                aws_bucket_name,
                intent_hist_filename,
                ExtraArgs={"ContentType": "image/png"},
            )
            intent_hist_url = "{}/{}/{}".format(
                s3_client.meta.endpoint_url, aws_bucket_name, intent_hist_filename
            )
        except ClientError as e:
            logger.error(e)

    return {"matrix_chart": confmat_url, "confidence_chart": intent_hist_url}


def entity_rasa_nlu_data(entity, evaluate):  # pragma: no cover
    return {
        "start": entity.start,
        "end": entity.end,
        "value": evaluate.text[entity.start : entity.end],
        "entity": entity.entity.value,
    }


def get_formatted_log(merged_logs):
    for merged_log in merged_logs:
        if "entities" in merged_log:
            entities = merged_log.get("entities")
            predicted_entities = merged_log.get("predicted_entities")
            merged_log["true_entities"] = []
            merged_log["false_positive_entities"] = []
            merged_log["swapped_error_entities"] = []
            for entity in entities:
                predicted_entity, is_entity_in_pred = is_entity_in_predicted(
                    entity, predicted_entities, True
                )
                swap_error_entity = is_start_end_in_list(entity, predicted_entities)
                if is_entity_in_pred:
                    entity["status"] = "success"
                    entity["confidence"] = predicted_entity.get("confidence")
                    merged_log["true_entities"].append(entity)
                elif swap_error_entity:
                    pred_entity_copy = swap_error_entity.copy()
                    pred_entity_copy["entity"] = entity.get("entity")
                    pred_entity_copy["predicted_entity"] = swap_error_entity.get(
                        "entity"
                    )
                    del pred_entity_copy["entity"]
                    merged_log["swapped_error_entities"].append(pred_entity_copy)
                else:
                    entity["status"] = "error"
                    merged_log["true_entities"].append(entity)

            for predicted_entity in predicted_entities:
                if not is_start_end_in_list(
                    predicted_entity, merged_log.get("true_entities")
                ) and not is_start_end_in_list(
                    predicted_entity, merged_log["swapped_error_entities"]
                ):
                    merged_log["false_positive_entities"].append(predicted_entity)
    return merged_logs


def merge_intent_entity_log(intent_evaluation, entity_evaluation):
    intent_logs = []
    entity_logs = []
    if intent_evaluation:
        intent_logs = intent_evaluation.get("log", [])
    if entity_evaluation:
        entity_logs = entity_evaluation.get("log", [])

    merged_logs = []
    for intent_log in intent_logs:
        for entity_log in entity_logs:
            if intent_log.get("text") == entity_log.get("text"):
                intent_log.update(entity_log)
        merged_logs.append(intent_log)

    return merged_logs


def evaluate_update(repository_version, repository_authorization):
    evaluations = backend().request_backend_start_evaluation(
        repository_version, repository_authorization
    )
    training_examples = []

    for evaluate in evaluations:
        training_examples.append(
            Message.build(
                text=evaluate.get("text"),
                intent=evaluate.get("intent"),
                entities=evaluate.get("entities"),
            )
        )

    test_data = TrainingData(training_examples=training_examples)
    interpreter = update_interpreters.get(
        repository_version, repository_authorization, rasa_version, use_cache=False
    )

    result = {
        "intent_evaluation": None,
        "entity_evaluation": None,
        "response_selection_evaluation": None,
    }

    intent_results, response_selection_results, entity_results, = get_eval_data(
        interpreter, test_data
    )

    if intent_results:
        result["intent_evaluation"] = evaluate_intents(intent_results)

    if entity_results:
        extractors = get_entity_extractors(interpreter)
        result["entity_evaluation"] = evaluate_entities(entity_results, extractors)

    intent_evaluation = result.get("intent_evaluation")
    entity_evaluation = result.get("entity_evaluation")

    merged_logs = merge_intent_entity_log(intent_evaluation, entity_evaluation)
    log = get_formatted_log(merged_logs)

    charts = plot_and_save_charts(repository_version, intent_results)
    evaluate_result = backend().request_backend_create_evaluate_results(
        {
            "repository_version": repository_version,
            "matrix_chart": charts.get("matrix_chart"),
            "confidence_chart": charts.get("confidence_chart"),
            "log": json.dumps(log),
            "intentprecision": intent_evaluation.get("precision"),
            "intentf1_score": intent_evaluation.get("f1_score"),
            "intentaccuracy": intent_evaluation.get("accuracy"),
            "entityprecision": entity_evaluation.get("precision"),
            "entityf1_score": entity_evaluation.get("f1_score"),
            "entityaccuracy": entity_evaluation.get("accuracy"),
        },
        repository_authorization,
    )

    intent_reports = intent_evaluation.get("report", {})
    entity_reports = entity_evaluation.get("report", {})

    for intent_key in intent_reports.keys():
        if intent_key and intent_key not in excluded_itens:
            intent = intent_reports.get(intent_key)

            backend().request_backend_create_evaluate_results_intent(
                {
                    "evaluate_id": evaluate_result.get("evaluate_id"),
                    "precision": intent.get("precision"),
                    "recall": intent.get("recall"),
                    "f1_score": intent.get("f1-score"),
                    "support": intent.get("support"),
                    "intent_key": intent_key,
                },
                repository_authorization,
            )

    for entity_key in entity_reports.keys():
        if entity_key and entity_key not in excluded_itens:  # pragma: no cover
            entity = entity_reports.get(entity_key)

            backend().request_backend_create_evaluate_results_score(
                {
                    "evaluate_id": evaluate_result.get("evaluate_id"),
                    "repository_version": repository_version,
                    "precision": entity.get("precision"),
                    "recall": entity.get("recall"),
                    "f1_score": entity.get("f1-score"),
                    "support": entity.get("support"),
                    "entity_key": entity_key,
                },
                repository_authorization,
            )

    return {
        "id": evaluate_result.get("evaluate_id"),
        "version": evaluate_result.get("evaluate_version"),
        "cross_validation": False
    }
