from bothub_nlp_rasa_utils import train


def send_job_ai_plataform(repository_version, by, repository_authorization):
    training_inputs = {
        'scaleTier': 'BASIC',
        'masterConfig': {
            "imageUri": 'gcr.io/bothub-273521/quickstart-image@sha256:f532b87cbb1c5db47586cff35a4afdfc3fefc23c3b8ad3174ef7688b3c503e8e',
        },
        'packageUris': [
            'gs://poc-training-ai-platform/job-dir/packages/82add65c49cb4a75897aec4b3832299824e68d494a47be7599d4904bace93912/ai-platform-poc-0.1.tar.gz'],
        'pythonModule': 'trainer.task',
        'args': ['--dataset', 'iac2.md', '--config', 'diet-pipeline2.yml'],
        'region': 'us-east1',
        'jobDir': 'gs://poc-training-ai-platform/job-dir',
    }

    job_spec = {'jobId': 'my_training_job_3', 'trainingInput': training_inputs}

    # Salve o ID do projeto no formato necessário para as APIs, "projects/projectname":
    project_name = 'bothub-273521'
    project_id = 'projects/{}'.format(project_name)

    # Consiga uma representação em Python dos serviços do AI Platform Training:
    cloudml = discovery.build('ml', 'v1')

    # Crie e envie sua solicitação:
    request = cloudml.projects().jobs().create(body=job_spec,
                                               parent=project_id)

    try:
        response = request.execute()
        print("SUCCESS!!!")
        return response

    except errors.HttpError as err:
        logging.error('/n There was an error creating the training job.'
                      ' Check the details:')
        logging.error(err._get_reason())


def train_update(repository_version, by, repository_authorization):  # pragma: no cover
    if settings.GOOGLE:
        send_job_ai_plataform(repository_version, by, repository_authorization)
    else:
        train.train_update(repository_version, by, repository_authorization)
