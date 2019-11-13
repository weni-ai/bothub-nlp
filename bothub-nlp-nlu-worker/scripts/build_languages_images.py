import json
import os
import subprocess

LANGUAGES_LIST = json.loads(os.environ.get('SUPPORTED_LANGUAGES'))

# {
#     "pt_br":
#         {
#             "install_from_pip": True,
#             "package_name": "pt_br_vectors_web_md",
#             "url_model": "url.tar.gz"
#         },
#     "fr":
#         {
#             "install_from_pip": False,
#             "package_name": "fr_core_news_md",
#             "url_model": ""
#         },
#     "pt":
#         {
#             "install_from_pip": False,
#             "package_name": "",
#             "url_model": ""
#         }
# }

for language in LANGUAGES_LIST:
    if LANGUAGES_LIST[language]['install_from_pip']:
        lang = f"{language}:pip+{LANGUAGES_LIST[language]['package_name']}:{LANGUAGES_LIST[language]['url_model']}"

        subprocess.call(
            [
                'docker-compose',
                'build',
                '--build-arg',
                f'DOWNLOAD_SPACY_MODELS="{lang}"',
                'bothub-nlp-nlu-worker'
             ]
        )

    elif not LANGUAGES_LIST[language]['install_from_pip'] and len(LANGUAGES_LIST[language]['package_name']) == 0:
        subprocess.call(
            [
                'docker-compose',
                'build',
                '--build-arg',
                f'DOWNLOAD_SPACY_MODELS="{language}"',
                'bothub-nlp-nlu-worker'
            ]
        )
    else:
        lang = f"{language}:{LANGUAGES_LIST[language]['package_name']}"

        subprocess.call(
            [
                'docker-compose',
                'build',
                '--build-arg',
                f'DOWNLOAD_SPACY_MODELS="{lang}"',
                'bothub-nlp-nlu-worker'
            ]
        )


for language in LANGUAGES_LIST:
    subprocess.call(
        [
            'docker',
            'push',
            f'{os.environ.get("BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME")}:{language}'
        ]
    )


