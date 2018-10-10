from setuptools import setup, find_packages


setup(
    name='bothub-nlp',
    version='1.0.0',
    description='Bothub NLP service',
    packages=find_packages(),
    install_requires=[
        'bothub-engine==1.16.0',
        'tornado==5.1.1',
        'contextvars==2.3',
        'raven==6.9.0',
        'spacy==2.0.12',
        'rasa-nlu==0.13.1',
        'tensorflow==1.11.0',
        'scikit-learn==0.20.0',
        'sklearn-crfsuite==0.3.6',
        'plac==0.9.6',
    ],
    python_requires='>=3.6',
)
