from collections import OrderedDict
from .debug_parse import DebugSentenceLime
from .utils import update_interpreters
from .utils import backend


def order_by_confidence(l):
    return sorted(
        l,
        key=lambda x: (x.get("confidence") is not None, x.get("confidence")),
        reverse=True,
    )


def minimal_entity(entity, self_flag=False):
    out = {
        "value": entity.get("value"),
        "entity": entity.get("entity"),
        "confidence": entity.get("confidence"),
    }

    if self_flag:
        out.update({"self": True})

    return out


def position_match(a, b):
    if a.get("start") is not b.get("start"):
        return False
    if a.get("end") is not b.get("end"):
        return False
    return True


def format_parse_output(repository_version, r, repository_authorization):
    intent = r.get("intent", None)
    intent_ranking = r.get("intent_ranking")
    labels_as_entity = r.get("labels_as_entity")
    extracted_entities = r.get("entities")

    entities = labels_as_entity

    for entity in extracted_entities:
        replaced = False
        for i, label in enumerate(labels_as_entity):
            if position_match(entity, label):
                entities[i] = entity
                replaced = True
                break
        if not replaced:
            entities.append(entity)

    entities_dict = {}

    for entity in reversed(order_by_confidence(entities)):
        label_value = "other"
        is_label = entity.get("label_as_entity", False)
        if is_label:
            label_value = entity.get("entity")
        else:
            repository_entity = backend().request_backend_repository_entity_nlu_parse(
                repository_version, repository_authorization, entity.get("entity")
            )
            if repository_entity.get("label"):
                label_value = repository_entity.get("label_value")

        if not entities_dict.get(label_value):
            entities_dict[label_value] = []

        entities_dict[label_value].append(minimal_entity(entity, is_label))

    out = OrderedDict(
        [
            ("intent", intent),
            ("intent_ranking", intent_ranking),
            ("labels_list", list(entities_dict.keys())),
            (
                "entities_list",
                list(
                    OrderedDict.fromkeys([x.get("entity") for x in extracted_entities])
                ),
            ),
            ("entities", entities_dict),
        ]
    )
    return out


def get_intention_list(repository_authorization):
    info = backend().request_backend_parse("info", repository_authorization)
    if not info.get('detail'):
        return info["intents_list"]


def parse_text(
    repository_version, repository_authorization, text, rasa_format=False, use_cache=True, is_debug=False
):
    interpreter = update_interpreters.get(
        repository_version, repository_authorization, use_cache=use_cache
    )
    if is_debug:
        intention_names = get_intention_list(repository_authorization)

        return DebugSentenceLime(interpreter, intention_names).get_result_per_word(text, 200)
    else:
        r = interpreter.parse(text)

        if rasa_format:
            return r

        return format_parse_output(repository_version, r, repository_authorization)

