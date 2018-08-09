from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity


EXAMPLES_MOCKUP = [
    {
        'text': 'hey',
        'intent': 'greet',
    },
    {
        'text': 'hey there',
        'intent': 'greet',
    },
    {
        'text': 'hello',
        'intent': 'greet',
    },
    {
        'text': 'hi',
        'intent': 'greet',
    },
    {
        'text': 'hello, my name is Douglas',
        'intent': 'greet',
        'entities': [
            {
                'start': 18,
                'end': 25,
                'entity': 'name',
            },
        ]
    },
    {
        'text': 'hi, my name is Douglas',
        'intent': 'greet',
        'entities': [
            {
                'start': 15,
                'end': 22,
                'entity': 'name',
            },
        ]
    },
    {
        'text': 'my name is Douglas',
        'intent': 'greet',
        'entities': [
            {
                'start': 11,
                'end': 18,
                'entity': 'name',
            },
        ]
    },
    {
        'text': 'bye',
        'intent': 'goodbye',
    },
    {
        'text': 'goodbye',
        'intent': 'goodbye',
    },
    {
        'text': 'good bye',
        'intent': 'goodbye',
    },
]


EXAMPLES_WITH_LABEL_MOCKUP = [
    {
        'text': 'I love my dog, my puppy is awesome',
        'intent': '',
        'entities': [
            {
                'start': 10,
                'end': 13,
                'entity': 'dog',
                'label': 'animal',
            },
            {
                'start': 27,
                'end': 34,
                'entity': 'dog',
                'label': 'animal',
            },
            {
                'start': 0,
                'end': 1,
                'entity': 'i',
                'label': 'person',
            }
        ],
    },
    {
        'text': 'We love dogs!',
        'intent': '',
        'entities': [
            {
                'start': 8,
                'end': 12,
                'entity': 'dog',
                'label': 'animal',
            },
            {
                'start': 0,
                'end': 2,
                'entity': 'we',
                'label': 'person',
            }
        ],
    },
    {
        'text': 'We have a cat, cats are beautiful',
        'intent': '',
        'entities': [
            {
                'start': 10,
                'end': 13,
                'entity': 'cat',
                'label': 'animal',
            },
            {
                'start': 15,
                'end': 19,
                'entity': 'cat',
                'label': 'animal',
            },
            {
                'start': 0,
                'end': 2,
                'entity': 'we',
                'label': 'person',
            }
        ],
    },
    {
        'text': 'I love my cat',
        'intent': '',
        'entities': [
            {
                'start': 10,
                'end': 13,
                'entity': 'cat',
                'label': 'animal',
            },
            {
                'start': 0,
                'end': 1,
                'entity': 'i',
                'label': 'person',
            }
        ]
    },
    {
        'text': 'I love my aunt',
        'intent': '',
        'entities': [
            {
                'start': 10,
                'end': 14,
                'entity': 'aunt',
                'label': 'person',
            },
            {
                'start': 0,
                'end': 1,
                'entity': 'i',
                'label': 'person',
            }
        ],
    },
    {
        'text': 'My aunt love cats',
        'intent': '',
        'entities': [
            {
                'start': 3,
                'end': 7,
                'entity': 'aunt',
                'label': 'person',
            },
            {
                'start': 13,
                'end': 17,
                'entity': 'cat',
                'label': 'animal',
            }
        ],
    },
]


def fill_examples(examples_mockup, repository, language=None):
    for example_mockup in examples_mockup:
        example = RepositoryExample.objects.create(
            repository_update=repository.current_update(
                (language or repository.language)),
            text=example_mockup.get('text'),
            intent=example_mockup.get('intent'))
        for entity_mockup in example_mockup.get('entities', []):
            example_entity = RepositoryExampleEntity.objects.create(
                repository_example=example,
                start=entity_mockup.get('start'),
                end=entity_mockup.get('end'),
                entity=entity_mockup.get('entity'))
            entity_label = entity_mockup.get('label')
            if entity_label:
                example_entity.entity.set_label(entity_label)
                example_entity.entity.save()
