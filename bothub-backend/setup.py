from setuptools import setup, find_packages


setup(
    name='bothub_backend',
    version='0.0.1',
    description='Bothub NLP Backend',
    packages=find_packages(),
    install_requires=[
        'requests==2.20.1',
    ],
)
