from platform import python_version
from typing import Dict

from pydantic import BaseModel

from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.service_definition.definition import (
    ServiceFoundryBuildDefinition,
    ServiceFoundryDefinition,
)
from servicefoundry.sfy_init.pack import Pack


class Parameters(BaseModel):
    name: str
    workspace: str


class MagicPack(Pack):
    def __init__(
        self,
        python_file: str,
        additional_requirements: Dict[str],
        parameters: Parameters,
    ):
        self.python_file = python_file
        self.additional_requirements = additional_requirements
        self.parameters = parameters

    def get_default_service_name(self):
        return "should-be-changed"

    def get_description(self):
        return None

    def ask_questions(self, input_hook: InputHook, output_hook: OutputCallBack):
        pass

    def get_default_definition(self) -> ServiceFoundryDefinition:
        definition = super().get_default_definition()
        definition.service.name = self.parameters.name
        definition.service.workspace = self.parameters.workspace
        definition.build = ServiceFoundryBuildDefinition(
            build_pack="sfy_build_pack_python",
            options={"python_version": f"python:{python_version()}"},
        )
        return definition
