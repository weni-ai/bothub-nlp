import docker
import configparser
import cgi

from time import sleep, time
from decouple import config
from celery_worker_on_demand import CeleryWorkerOnDemand
from celery_worker_on_demand import Agent
from celery_worker_on_demand import UpWorker
from celery_worker_on_demand import DownWorker
from celery_worker_on_demand import APIHandler

from . import settings


LABEL_KEY = "bothub-nlp-wod.name"
EMPTY = "empty-value"
ENV_LIST = [
    "{}={}".format(var, config(var, default=EMPTY))
    for var in [
        "ENVIRONMENT",
        "SUPPORTED_LANGUAGES",
        "BOTHUB_ENGINE_URL",
        "BOTHUB_NLP_CELERY_SENTRY_CLIENT",
        "BOTHUB_NLP_CELERY_SENTRY",
        "BOTHUB_NLP_CELERY_BROKER_URL",
        "BOTHUB_NLP_CELERY_BACKEND_URL",
        "BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE",
        "BOTHUB_NLP_AWS_S3_BUCKET_NAME",
        "BOTHUB_NLP_AWS_ACCESS_KEY_ID",
        "BOTHUB_NLP_AWS_SECRET_ACCESS_KEY",
        "BOTHUB_NLP_AWS_REGION_NAME",
    ]
]

docker_client = docker.DockerClient(base_url=settings.BOTHUB_NLP_DOCKER_CLIENT_BASE_URL)
running_services = {}
last_services_lookup = 0


def services_lookup():
    global running_services
    global last_services_lookup
    if (time() - last_services_lookup) < 5:
        return False
    running_services = {}
    for service in docker_client.services.list():
        service_labels = service.attrs.get("Spec", {}).get("Labels")
        if LABEL_KEY in service_labels:
            queue_name = service_labels.get(LABEL_KEY)
            running_services[queue_name] = service
    last_services_lookup = time()
    return True


class MyUpWorker(UpWorker):
    def run(self):
        global running_services
        services_lookup()
        service = running_services.get(self.queue.name)
        if not service:
            queue_language = (
                self.queue.name.split(":")[1]
                if ":" in self.queue.name
                else self.queue.name
            )
            constraints = []
            if settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE:
                constraints.append("node.role == worker")
            docker_client.services.create(
                settings.BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME + f":{queue_language}",
                [
                    "celery",
                    "worker",
                    "--autoscale",
                    "5,3",
                    "-O",
                    "fair",
                    "--workdir",
                    "bothub_nlp_nlu_worker",
                    "-A",
                    "celery_app",
                    "-c",
                    "1",
                    "-l",
                    "INFO",
                    "-E",
                    "-Q",
                    self.queue.name,
                ],
                env=list(
                    list(filter(lambda v: not v.endswith(EMPTY), ENV_LIST)) +
                    list([f'BOTHUB_NLP_LANGUAGE_QUEUE={self.queue.name}']) +
                    list(['BOTHUB_NLP_SERVICE_WORKER=true'])
                ),
                labels={LABEL_KEY: self.queue.name},
                networks=settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS,
                constraints=constraints,
            )
        while not self.queue.has_worker:
            sleep(1)


class MyDownWorker(DownWorker):
    def run(self):
        global running_services
        services_lookup()
        service = running_services.get(self.queue.name)
        service.remove()
        running_services[self.queue.name] = None


class MyAgent(Agent):
    def flag_down(self, queue):
        global running_services
        ignore_list = self.cwod.config.get("worker-down", "ignore").split(",")
        if queue.name in ignore_list:
            return False
        if queue.size > 0:
            return False
        if not queue.has_worker:
            return False
        services_lookup()
        service = running_services.get(queue.name)
        if not service:
            return False
        last_interaction = 0
        for worker in queue.workers:
            last_interaction = sorted(
                [
                    last_interaction,
                    (worker.last_task_received_at or 0),
                    (worker.last_task_started_at or 0),
                    (worker.last_task_succeeded_at or 0),
                ],
                reverse=True,
            )[0]
        if last_interaction == 0:
            return False
        last_interaction_diff = time() - last_interaction
        if last_interaction_diff > (
            settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_DOWN_TIME * 60
        ):
            return True
        return False


class MyAPIHandler(APIHandler):
    def post_data(self):
        content_type = self.headers.get("content-type")
        if not content_type:
            return {}
        ctype, pdict = cgi.parse_header(content_type)
        if not ctype == "multipart/form-data":
            return {}
        pdict["boundary"] = bytes(pdict.get("boundary", ""), "utf-8")
        parsed = cgi.parse_multipart(self.rfile, pdict)
        return dict(
            map(
                lambda x: (
                    x[0],
                    list(map(lambda x: x.decode(), x[1]))
                    if len(x[1]) > 1
                    else x[1][0].decode(),
                ),
                parsed.items(),
            )
        )

    def do_POST(self):
        if not self.has_permission():
            return
        post_data = self.post_data()
        for key, value in post_data.items():
            section, option = key.split(".", 1)
            self.cwod.config.set(
                section, option, ",".join(value) if isinstance(value, list) else value
            )
        self.cwod.write_config()
        self.do_GET()


class MyDemand(CeleryWorkerOnDemand):
    Agent = MyAgent
    UpWorker = MyUpWorker
    DownWorker = MyDownWorker
    APIHandler = MyAPIHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read_dict({"worker-down": {"ignore": []}})
        self.config.read(settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE)

    def write_config(self):
        self.config.write(
            open(settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE, "w+")
        )

    def serializer(self):
        data = super().serializer()
        data.update({"config": self.config._sections})
        return data
