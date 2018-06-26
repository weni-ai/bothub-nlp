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


def fill_examples(examples_mockup, repository, language=None):
    for example_mockup in examples_mockup:
        example = RepositoryExample.objects.create(
            repository_update=repository.current_update(
                (language or repository.language)),
            text=example_mockup.get('text'),
            intent=example_mockup.get('intent'))
        for entity_mockup in example_mockup.get('entities', []):
            RepositoryExampleEntity.objects.create(
                repository_example=example,
                start=entity_mockup.get('start'),
                end=entity_mockup.get('end'),
                entity=entity_mockup.get('entity'))
