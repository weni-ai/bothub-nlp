from unidecode import unidecode
import re
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.training_data import Message, TrainingData


class Preprocessing(Component):

    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""

        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {"language": None}

    def __init__(
        self, component_config: Optional[Dict[Text, Any]] = None, language: str = None
    ) -> None:
        super().__init__(component_config)
        self.language = component_config.get("language")

    def portuguese_preprocesing(self, phrase):

        phrase = phrase.replace("blza", "beleza")
        phrase = phrase.replace("flw", "falou")
        phrase = phrase.replace("vlw", "valeu")
        phrase = phrase.replace("ok", "okay")
        phrase = phrase.replace("tranks", "tranquilo")
        phrase = phrase.replace("mkt", "marketing")

        # set regex to "blz"
        blz_regex = r"\b(bl)z*\b"
        # set regex for "n":
        n_regex = r"\b(n|N)\1*\b"
        # set regex for "s":
        s_regex = r"\b(s|S)\1*\b"
        # set regex for "to":
        to_regex = r"\b(t)o*\b"
        # set regex for "ta":
        ta_regex = r"\b(t)o*\b"
        # set regex for "mkt":
        mkt_regex = r"\b(mkt)\b"
        # set regex for "ok":
        ok_regex = r"\b(ok)\b"
        # set regex for "bd":
        bd_regex = r"\b(bd)\b"

        # set replace words
        S_WORD = "sim"
        N_WORD = "nao"
        BLZ_WORD = "beleza"
        TO_WORD = "estou"
        TA_WORD = "esta"
        MKT_WORD = "marketing"
        OK_WORD = "okay"
        BD_WORD = "bom dia"

        # replace regex by S_WORD"
        phrase = re.sub(s_regex, S_WORD, phrase)
        # replace regex by N_WORD
        phrase = re.sub(n_regex, N_WORD, phrase)
        # replace regex by BLZ_WORD
        phrase = re.sub(blz_regex, BLZ_WORD, phrase)
        # replace regex by TO_WORD
        phrase = re.sub(to_regex, TO_WORD, phrase)
        # replace regex by TA_WORD
        phrase = re.sub(ta_regex, TA_WORD, phrase)
        # replace regex by MKT_WORD
        phrase = re.sub(mkt_regex, MKT_WORD, phrase)
        # replace regex by OK_WORD
        phrase = re.sub(ok_regex, OK_WORD, phrase)
        # replace regex by BD_WORD
        phrase = re.sub(bd_regex, BD_WORD, phrase)

        return phrase

    def english_preprocesing(self, phrase):
        # set regex for "mkt":
        mkt_regex = r"\b(mkt)\b"
        # set regex for "ok":
        ok_regex = r"\b(ok)\b"
        # set regex for "ty":
        ty_regex = r"\b(ty)\b"
        # set regex for "thx":
        thx_regex = r"\b(thx)\b"
        # set regex for "tks":
        tks_regex = r"\b(tks)\b"
        # set regex for " 'm / 'mmmm ":
        am_regex = r"('m)m*\b"
        # set regex for " 'm / 'mmmm ":
        are_regex = r"('re)e*\b"
        # set regex for " *n't ":
        not_regex = r"(n't)\b"

        # set replace words
        MKT_WORD = "marketing"
        OK_WORD = "okay"
        TY_WORD = "thank you"
        AM_WORD = " am"
        ARE_WORD = " are"
        NOT_WORD = " not"

        # replace regex by MKT_WORD
        phrase = re.sub(mkt_regex, MKT_WORD, phrase)
        # replace regex by OK_WORD
        phrase = re.sub(ok_regex, OK_WORD, phrase)
        # replace regex by TY_WORD
        phrase = re.sub(ty_regex, TY_WORD, phrase)
        # replace regex by THX_WORD
        phrase = re.sub(thx_regex, TY_WORD, phrase)
        # replace regex by TKS_WORD
        phrase = re.sub(tks_regex, TY_WORD, phrase)
        # replace regex by AM_WORD
        phrase = re.sub(am_regex, AM_WORD, phrase)
        # replace regex by ARE_WORD
        phrase = re.sub(are_regex, ARE_WORD, phrase)
        # replace regex by NOT_WORD
        phrase = re.sub(not_regex, NOT_WORD, phrase)

        return phrase

    @classmethod
    def create(
        cls, component_config: Dict[Text, Any], config: RasaNLUModelConfig
    ) -> "Preprocessing":
        # component_config = override_defaults(cls.defaults, component_config)
        language = config.language
        return cls(component_config, language)

    def provide_context(self) -> Dict[Text, Any]:
        return {"language": self.language}

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Train this component"""
        not_repeated_phrases = set()
        size = len(training_data.training_examples)
        subtract_idx = 0

        for idx in range(size):
            example_text = training_data.training_examples[idx - subtract_idx].text
            # removing accent and lowercasing characters
            example_text = unidecode(example_text.lower())

            if config.language == "en":
                example_text = self.english_preprocesing(example_text)

            if config.language == "pt_br":
                example_text = self.portuguese_preprocesing(example_text)

            if example_text in not_repeated_phrases:
                # remove example at this index from training_examples
                training_data.training_examples.pop(idx - subtract_idx)
                subtract_idx += 1
            else:
                not_repeated_phrases.add(example_text)
                training_data.training_examples[idx - subtract_idx].text = example_text

    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message."""
        APOSTROPHE_OPTIONS = ["'", "`"]

        # removing accent and lowercasing characters
        message.text = unidecode(message.text.lower())
        # remove apostrophe from the phrase (important be first than s_regex regex)
        for APOSTROPHE in APOSTROPHE_OPTIONS:
            message.text = message.text.replace(APOSTROPHE, "")

        if self.language == "en":
            message.text = self.english_preprocesing(message.text)

        if self.language == "pt_br":
            message.text = self.portuguese_preprocesing(message.text)
