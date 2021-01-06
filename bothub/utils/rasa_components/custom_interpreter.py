from rasa.nlu.model import Metadata, Interpreter
from rasa.nlu.components import Component, ComponentBuilder
from typing import Any, Dict, List, Text, Optional


class CustomInterpreter(Interpreter):
    """Use a trained pipeline of components to parse text messages."""
    def __init__(
        self,
        pipeline: List[Component],
        context: Optional[Dict[Text, Any]],
        model_metadata: Optional[Metadata] = None
    ) -> None:

        super().__init__(pipeline, context, model_metadata)

    @staticmethod
    def load(
        model_dir: Text,
        component_builder: Optional[ComponentBuilder] = None,
        skip_validation: bool = False,
    ) -> "Interpreter":
        """Create an interpreter based on a persisted model.

        Args:
            skip_validation: If set to `True`, tries to check that all
                required packages for the components are installed
                before loading them.
            model_dir: The path of the model to load
            component_builder: The
                :class:`rasa.nlu.components.ComponentBuilder` to use.

        Returns:
            An interpreter that uses the loaded model.
        """

        model_metadata = Metadata.load(model_dir)

        # Adapt Loader to accept new component-name (changed) with older models
        metadata = model_metadata.__dict__['metadata']
        for i in range(len(metadata['pipeline'])):
            component_name = metadata['pipeline'][i]['class']
            if 'bothub_nlp_rasa_utils' in component_name:
                metadata['pipeline'][i]['class'] = component_name.replace('bothub_nlp_rasa_utils', 'bothub.utils', 1)

        model_metadata = Metadata(metadata, model_dir)

        Interpreter.ensure_model_compatibility(model_metadata)
        return Interpreter.create(model_metadata, component_builder, skip_validation)
