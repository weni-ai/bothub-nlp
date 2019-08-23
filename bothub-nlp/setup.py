from setuptools import setup, find_packages


setup(
    name='bothub-nlp',
    version='0.2.0',
    description='Bothub NLP Common',
    packages=find_packages(),
    # dependency_links=[
    #     'git+https://github.com/Ilhasoft/bothub-engine@1.21.0#egg=bothub-en' +
    #     'gine',
    # ],
    install_requires=[
        'python-decouple==3.1',
        'requests==2.20.1',
    ],
)
