from setuptools import setup, find_packages


setup(
    name='bothub-nlp',
    version='1.3.1',
    description='Bothub NLP service',
    packages=find_packages(),
    dependency_links=[
        'git+https://github.com/Ilhasoft/bothub-engine@1.17.0#egg=bothub-en' +
        'gine',
        'git+https://github.com/Ilhasoft/celery-worker-on-demand@0.1.2#egg=' +
        'celery-worker-on-demand',
    ],
    install_requires=[
        'tornado==5.1.1',
        'contextvars==2.3',
        'raven==6.9.0',
        'spacy==2.0.18',
        'rasa-nlu==0.13.8',
        'tensorflow==1.12.0',
        'scikit-learn==0.20.1',
        'sklearn-crfsuite==0.3.6',
        'plac==0.9.6',
        'celery==4.2.1',
        'docker==3.6.0',
    ],
    python_requires='>=3.4',
)
