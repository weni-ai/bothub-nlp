from collections import defaultdict
from rasa.nlu.test import plot_histogram, IntentEvaluationResult, determine_token_labels
from rasa.nlu.model import Interpreter


class BothubInterpreter(Interpreter):
    @staticmethod
    def default_output_attributes():
        return {
            "intent": {"name": None, "confidence": 0.0},
            "entities": [],
            "labels_as_entity": [],
        }


def get_entity_targets(test_data):
    """Extracts entity targets from the test data."""
    return [e.get("entities", []) for e in test_data.training_examples]


def get_intent_targets(test_data):  # pragma: no cover
    """Extracts intent targets from the test data."""
    return [e.get("intent", "") for e in test_data.training_examples]


def plot_intent_confidences(intent_results, intent_hist_filename):
    import matplotlib.pyplot as plt

    # create histogram of confidence distribution, save to file and display
    plt.gcf().clear()
    pos_hist = [r.confidence for r in intent_results if r.target == r.prediction]

    neg_hist = [r.confidence for r in intent_results if r.target != r.prediction]

    plot_histogram([pos_hist, neg_hist], intent_hist_filename)


def get_entity_predictions(interpreter, test_data):  # pragma: no cover
    """Runs the model for the test set and extracts entity
    predictions and tokens."""
    from . import logger

    entity_predictions, tokens = [], []
    for e in test_data.training_examples:
        res = interpreter.parse(e.text, only_output_properties=False)
        entity_predictions.append(res.get("entities", []))
        try:
            tokens.append(res["tokens"])
        except KeyError:
            logger.debug(
                "No tokens present, which is fine if you don't have a"
                " tokenizer in your pipeline"
            )
    return entity_predictions, tokens


def get_intent_predictions(targets, interpreter, test_data):  # pragma: no cover
    """Runs the model for the test set and extracts intent predictions.
        Returns intent predictions, the original messages
        and the confidences of the predictions"""
    intent_results = []
    for e, target in zip(test_data.training_examples, targets):
        res = interpreter.parse(e.text, only_output_properties=False)
        intent_results.append(
            IntentEvaluationResult(
                target,
                res.get("intent", {}).get("name"),
                res.get("text", {}),
                res.get("intent", {}).get("confidence"),
            )
        )

    return intent_results


def align_entity_predictions(targets, predictions, tokens, extractors):
    """Aligns entity predictions to the message tokens.

    Determines for every token the true label based on the
    prediction targets and the label assigned by each
    single extractor.

    :param targets: list of target entities
    :param predictions: list of predicted entities
    :param tokens: original message tokens
    :param extractors: the entity extractors that should be considered
    :return: dictionary containing the true token labels and token labels
             from the extractors
    """

    true_token_labels = []
    entities_by_extractors = {extractor: [] for extractor in extractors}
    for p in predictions:
        entities_by_extractors[p["extractor"]].append(p)
    extractor_labels = defaultdict(list)
    for t in tokens:
        true_token_labels.append(determine_token_labels(t, targets, None))
        for extractor, entities in entities_by_extractors.items():
            extracted = determine_token_labels(t, entities, extractor)
            extractor_labels[extractor].append(extracted)

    return {
        "target_labels": true_token_labels,
        "extractor_labels": dict(extractor_labels),
    }


def align_all_entity_predictions(targets, predictions, tokens, extractors):
    """ Aligns entity predictions to the message tokens for the whole dataset
        using align_entity_predictions

    :param targets: list of lists of target entities
    :param predictions: list of lists of predicted entities
    :param tokens: list of original message tokens
    :param extractors: the entity extractors that should be considered
    :return: list of dictionaries containing the true token labels and token
             labels from the extractors
    """

    aligned_predictions = []
    for ts, ps, tks in zip(targets, predictions, tokens):
        aligned_predictions.append(align_entity_predictions(ts, ps, tks, extractors))

    return aligned_predictions


def _targets_predictions_from(intent_results):
    return zip(*[(r.intent_target, r.intent_prediction) for r in intent_results])
