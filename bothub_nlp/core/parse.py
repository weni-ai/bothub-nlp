import pprint

from functools import reduce
from collections import OrderedDict

from bothub.common.models import RepositoryEntity

from . import updateInterpreters


pp = pprint.PrettyPrinter(indent=4)


def order_by_confidence(l):
    return sorted(
        l,
        key=lambda x: x.get('confidence'),
        reverse=True)


def entities_values(l):
    return list(set([
        x.get('entity')
        for x in l
    ]))


def minimal_entity(entity, self_flag=False):
    out = {
        'value': entity.get('value'),
        'entity': entity.get('entity'),
        'confidence': entity.get('confidence'),
        'start': entity.get('start'),
        'end': entity.get('end'),
    }

    if self_flag:
        out.update({'self': True})

    return out


def reduce_label_in_entities_base(current, label_as_entity):
    current.update({
        label_as_entity.get('entity'): [minimal_entity(
            label_as_entity,
            self_flag=True)],
    })
    return current


def entities_position_match(a, b):
    if a.get('start') is not b.get('start'):
        return False
    if a.get('end') is not b.get('end'):
        return False
    return True


def parse_text(update, text, rasa_format=False, use_cache=True):
    interpreter = updateInterpreters.get(update, use_cache=use_cache)
    r = interpreter.parse(text)

    if rasa_format:
        return r

    intent = r.get('intent', None)
    intent_ranking = r.get('intent_ranking')
    labels_as_entity = order_by_confidence(r.get('labels_as_entity'))
    extracted_entities = order_by_confidence(r.get('entities'))

    entities = reduce(
        reduce_label_in_entities_base,
        labels_as_entity,
        {
            'other': [],
        })
    for entity in reversed(extracted_entities):
        added = False
        repository_entity = RepositoryEntity.objects.get(
            repository=update.repository,
            value=entity.get('entity'))
        label_value = repository_entity.label.value \
            if repository_entity.label else 'other'
        current_label_items = list(entities.get(label_value))
        for i, label_item in enumerate(current_label_items):
            if entities_position_match(entity, label_item):
                entities[label_value][i] = minimal_entity(entity)
                added = True
                break
        if not added:
            entities[label_value].insert(0, minimal_entity(entity))

    out = OrderedDict([
        ('intent', intent),
        ('intent_ranking', intent_ranking),
        ('labels_list', entities_values(labels_as_entity)),
        ('entities_list', entities_values(extracted_entities)),
        ('entities', entities),
    ])
    return out
