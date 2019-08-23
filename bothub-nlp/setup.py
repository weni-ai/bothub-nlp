from setuptools import setup, find_packages


setup(
    name='bothub-nlp',
    version='0.2.0',
    description='Bothub NLP Common',
    packages=find_packages(),
    install_requires=[
        'python-decouple==3.1',
        'requests==2.20.1',
    ],
)
