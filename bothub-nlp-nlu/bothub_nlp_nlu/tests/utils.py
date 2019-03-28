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
        'text': 'I love cat',
        'intent': '',
        'entities': [
            {
                'start': 7,
                'end': 10,
                'entity': 'cat',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'I love dog',
        'intent': '',
        'entities': [
            {
                'start': 7,
                'end': 10,
                'entity': 'dog',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'I love turtle',
        'intent': '',
        'entities': [
            {
                'start': 7,
                'end': 13,
                'entity': 'turtle',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'My dad love cat',
        'intent': '',
        'entities': [
            {
                'start': 3,
                'end': 6,
                'entity': 'dad',
                'label': 'person',
            },
            {
                'start': 12,
                'end': 15,
                'entity': 'cat',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'My aunt love cat',
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
                'end': 16,
                'entity': 'cat',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'My sister love dog',
        'intent': '',
        'entities': [
            {
                'start': 3,
                'end': 9,
                'entity': 'sister',
                'label': 'person',
            },
            {
                'start': 15,
                'end': 18,
                'entity': 'dog',
                'label': 'animal',
            },
        ],
    },
]

EXAMPLES_WITH_SPACY_NER_MOCKUP = [
    {
        'text': 'Minha irmã ama cachorros',
        'intent': '',
        'entities': [
            {
                'start': 15,
                'end': 24,
                'entity': 'dog',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'Eu gosto de tartarugas',
        'intent': '',
        'entities': [
            {
                'start': 12,
                'end': 22,
                'entity': 'tartarugas',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'Meu pai ama gatos',
        'intent': '',
        'entities': [
            {
                'start': 12,
                'end': 17,
                'entity': 'cat',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'Minha tia ama gatos',
        'intent': '',
        'entities': [
            {
                'start': 14,
                'end': 19,
                'entity': 'cat',
                'label': 'animal',
            },
        ],
    },
    {
        'text': 'Minha irmã ama cachorros',
        'intent': '',
        'entities': [
            {
                'start': 15,
                'end': 24,
                'entity': 'dog',
                'label': 'animal',
            },
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
