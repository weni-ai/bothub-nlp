from bothub_nlp_celery.app import nlp_language
from rasa.nlu.config import override_defaults
from rasa.nlu.utils.spacy_utils import SpacyNLP as RasaNLUSpacyNLP


class SpacyNLP(RasaNLUSpacyNLP):
    @classmethod
    def load(
        cls, meta, model_dir=None, model_metadata=None, cached_component=None, **kwargs
    ):
        if cached_component:
            return cached_component

        cls.ensure_proper_language_model(nlp_language)
        return cls(meta, nlp_language)

    @classmethod
    def create(cls, component_config, config):
        component_config = override_defaults(cls.defaults, component_config)

        spacy_model_name = component_config.get("model")

        # if no model is specified, we fall back to the language string
        if not spacy_model_name:
            component_config["model"] = config.language

        cls.ensure_proper_language_model(nlp_language)
        return cls(component_config, nlp_language)
