from collections import OrderedDict

from bothub.common.models import RepositoryEntity

from . import update_interpreters


def order_by_confidence(l):
    return sorted(
        l,
        key=lambda x: x.get('confidence'),
        reverse=True)


def minimal_entity(entity, self_flag=False):
    out = {
        'value': entity.get('value'),
        'entity': entity.get('entity'),
        'confidence': entity.get('confidence'),
    }

    if self_flag:
        out.update({'self': True})

    return out


def position_match(a, b):
    if a.get('start') is not b.get('start'):
        return False
    if a.get('end') is not b.get('end'):
        return False
    return True


def format_parse_output(update, r):
    intent = r.get('intent', None)
    intent_ranking = r.get('intent_ranking')
    labels_as_entity = r.get('labels_as_entity')
    extracted_entities = r.get('entities')

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
        label_value = 'other'
        is_label = entity.get('label_as_entity', False)
        if is_label:
            label_value = entity.get('entity')
        else:
            repository_entity = RepositoryEntity.objects.get(
                repository=update.repository,
                value=entity.get('entity'))
            if repository_entity.label:
                label_value = repository_entity.label.value

        if not entities_dict.get(label_value):
            entities_dict[label_value] = []

        entities_dict[label_value].append(minimal_entity(entity, is_label))

    out = OrderedDict([
        ('intent', intent),
        ('intent_ranking', intent_ranking),
        (
            'labels_list',
            list(entities_dict.keys()),
        ),
        (
            'entities_list',
            list(set([
                x.get('entity')
                for x in extracted_entities
            ])),
        ),
        ('entities', entities_dict),
    ])
    return out


def parse_text(update, text, rasa_format=False, use_cache=True):
    interpreter = update_interpreters.get(update, use_cache=use_cache)
    r = interpreter.parse(text)

    if rasa_format:
        return r

    return format_parse_output(update, r)
