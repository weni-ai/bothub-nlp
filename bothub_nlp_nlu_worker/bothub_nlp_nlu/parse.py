from collections import OrderedDict
from rasa.nlu import __version__ as rasa_version
from .utils import update_interpreters


def order_by_confidence(l):
    return sorted(
        l,
        key=lambda x: (x.get("confidence") is not None, x.get("confidence")),
        reverse=True,
    )


def minimal_entity(entity, self_flag=False):  # pragma: no cover
    out = {
        "value": entity.get("value"),
        "entity": entity.get("entity"),
        "confidence": entity.get("confidence"),
        "start": entity.get("start"),
        "end": entity.get("end"),
    }

    if self_flag:
        out.update({"self": True})

    return out


def position_match(a, b):  # pragma: no cover
    if a.get("start") is not b.get("start"):
        return False
    if a.get("end") is not b.get("end"):
        return False
    return True


def format_parse_output(
    repository_version, r, repository_authorization
):  # pragma: no cover
    intent = r.get("intent", None)
    intent_ranking = r.get("intent_ranking")
    entities = r.get("entities")

    out = OrderedDict(
        [
            ("intent", intent),
            ("intent_ranking", intent_ranking),
            (
                "entities_list",
                list(OrderedDict.fromkeys([x.get("entity") for x in entities])),
            ),
            ("entities", entities),
        ]
    )
    return out


def parse_text(
    repository_version,
    repository_authorization,
    text,
    rasa_format=False,
    use_cache=True,
):
    interpreter = update_interpreters.get(
        repository_version, repository_authorization, rasa_version, use_cache=use_cache
    )
    r = interpreter.parse(text)

    if rasa_format:
        return r

    return format_parse_output(repository_version, r, repository_authorization)
