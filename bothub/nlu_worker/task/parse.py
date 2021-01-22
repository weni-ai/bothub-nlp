from collections import OrderedDict
from rasa.nlu import __version__ as rasa_version


def format_parse_output(
    repository_version, r, repository_authorization
):  # pragma: no cover
    intent = r.get("intent", None)
    intent_ranking = r.get("intent_ranking", [])
    entities = r.get("entities", [])

    out = OrderedDict(
        [
            ("intent", intent),
            ("intent_ranking", intent_ranking),
            (
                "entities_list",
                list(OrderedDict.fromkeys([x.get("entity", None) for x in entities])),
            ),
            ("entities", entities),
        ]
    )
    return out


def parse_text(
    repository_version,
    repository_authorization,
    interpreter_manager,
    text,
    rasa_format=False,
    use_cache=True,
):
    interpreter = interpreter_manager.get_interpreter(
        repository_version, repository_authorization, rasa_version, use_cache
    )
    r = interpreter.parse(text)

    if rasa_format:
        return r

    return format_parse_output(repository_version, r, repository_authorization)
