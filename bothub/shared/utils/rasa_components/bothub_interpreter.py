import datetime
from rasa.nlu.model import Metadata, Interpreter
from rasa.nlu.components import Component, ComponentBuilder
from rasa.nlu import components
from rasa.nlu.training_data import Message
from typing import Any, Dict, List, Text, Optional


class BothubInterpreter(Interpreter):
    """Use a trained pipeline of components to parse text messages."""

    def __init__(
        self,
        pipeline: List[Component],
        context: Optional[Dict[Text, Any]],
        model_metadata: Optional[Metadata] = None,
    ) -> None:

        super().__init__(pipeline, context, model_metadata)

    @staticmethod
    def load(
        model_dir: Text,
        component_builder: Optional[ComponentBuilder] = None,
        skip_validation: bool = False,
    ) -> "BothubInterpreter":
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
        metadata = model_metadata.__dict__["metadata"]
        for i in range(len(metadata["pipeline"])):
            component_name = metadata["pipeline"][i]["class"]
            if "bothub_nlp_rasa_utils" in component_name:
                metadata["pipeline"][i]["class"] = component_name.replace(
                    "bothub_nlp_rasa_utils", "bothub.shared.utils", 1
                )

        model_metadata = Metadata(metadata, model_dir)

        BothubInterpreter.ensure_model_compatibility(model_metadata)
        return BothubInterpreter.create(model_metadata, component_builder, skip_validation)

    @staticmethod
    def create(
        model_metadata: Metadata,
        component_builder: Optional[ComponentBuilder] = None,
        skip_validation: bool = False,
    ) -> "BothubInterpreter":
        """Load stored model and components defined by the provided metadata."""

        context = {}

        if component_builder is None:
            # If no builder is passed, every interpreter creation will result
            # in a new builder. hence, no components are reused.
            component_builder = components.ComponentBuilder()

        pipeline = []

        # Before instantiating the component classes,
        # lets check if all required packages are available
        if not skip_validation:
            components.validate_requirements(model_metadata.component_classes)

        for i in range(model_metadata.number_of_components):
            component_meta = model_metadata.for_component(i)
            component = component_builder.load_component(
                component_meta, model_metadata.model_dir, model_metadata, **context
            )
            try:
                updates = component.provide_context()
                if updates:
                    context.update(updates)
                pipeline.append(component)
            except components.MissingArgumentError as e:
                raise Exception(
                    "Failed to initialize component '{}'. "
                    "{}".format(component.name, e)
                )

        return BothubInterpreter(pipeline, context, model_metadata)

    def parse(
        self,
        text: Text,
        time: Optional[datetime.datetime] = None,
        only_output_properties: bool = True,
    ) -> Dict[Text, Any]:
        """Parse the input text, classify it and return pipeline result.
        The pipeline result usually contains intent and entities."""

        if not text.replace(" ", ""):
            # Not all components are able to handle empty strings. So we need
            # to prevent that... This default return will not contain all
            # output attributes of all components, but in the end, no one
            # should pass an empty string in the first place.
            output = self.default_output_attributes()
            output['intent_ranking'] = []
            output["text"] = ""

            return output

        message = Message(text, self.default_output_attributes(), time=time)

        for component in self.pipeline:
            component.process(message, **self.context)

        output = self.default_output_attributes()
        output.update(message.as_dict(only_output_properties=only_output_properties))

        return output
