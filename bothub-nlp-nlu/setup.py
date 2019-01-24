from setuptools import setup, find_packages


setup(
    name='bothub-nlp-nlu',
    version='0.2.0',
    description='Bothub NLP NLU',
    packages=find_packages(),
    dependency_links=[
        'git+https://github.com/Ilhasoft/bothub-engine@1.19.0b#egg=bothub-en' +
        'gine',
    ],
    install_requires=[
        'contextvars==2.3',
        'spacy==2.0.18',
        'rasa-nlu==0.14.1',
        'tensorflow==1.12.0',
        'scikit-learn==0.20.2',
        'sklearn-crfsuite==0.3.6',
        'pythainlp==1.7.2',
        'pymorphy2==0.8',
        'plac==0.9.6',
    ],
)
