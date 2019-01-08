from setuptools import setup, find_packages


setup(
    name='bothub-nlp',
    version='0.1.0',
    description='Bothub NLP Common',
    packages=find_packages(),
    dependency_links=[
        'git+https://github.com/Ilhasoft/bothub-engine@1.17.0#egg=bothub-en' +
        'gine',
    ],
    install_requires=[
        'python-decouple==3.1',
    ],
)
