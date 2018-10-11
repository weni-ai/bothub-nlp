#!/usr/bin/env python
from tempfile import NamedTemporaryFile
from decouple import config


languages = config('SUPPORTED_LANGUAGES')
dockerfile = NamedTemporaryFile(prefix='Dockerfile', delete=False)
dockerfile.write(b'FROM python:3.6.6\n')
dockerfile.write(b'ENV WORKDIR /home/app\n')
dockerfile.write(b'ENV IS_PRODUCTION true\n')
dockerfile.write(b'ENV PORT 2657\n')
dockerfile.write(b'WORKDIR $WORKDIR\n')
dockerfile.write(b'RUN pip install pipenv psycopg2-binary\n')
dockerfile.write(b'COPY Pipfile .\n')
dockerfile.write(b'COPY Pipfile.lock .\n')
dockerfile.write(b'COPY Makefile .\n')
dockerfile.write(b'RUN make -s check_environment\n')
dockerfile.write(b'COPY . .\n')
dockerfile.write(b'ARG DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD\n')
if languages:
    for language in languages.split('|'):
        line = 'RUN python scripts/download_spacy_models.py {}\n'.format(
            language)
        dockerfile.write(bytes(line, 'utf8'))
dockerfile.write(b'ENV DOWNLOADED_LANGUAGES ' +
                 b'${DOWNLOAD_LANGUAGES_ON_DOCKER_IMAGE_BUILD}\n')
dockerfile.write(b'RUN make -s import_ilha_spacy_langs '
                 b'CHECK_ENVIRONMENT=false\n')
dockerfile.write(b'RUN chmod +x ./entrypoint.sh\n')
dockerfile.write(b'ENTRYPOINT $WORKDIR/entrypoint.sh\n')
print(dockerfile.name)
