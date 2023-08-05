from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.io.parameters import Parameter, WorkspaceParameter
from servicefoundry.service_definition.definition import (
    CPU,
    Memory,
    Port,
    ServiceFoundryDefinition,
    ServiceFoundryServiceDefinition,
)


class ServiceFoundryDefinitionGenerator:
    def __init__(self, input_hook: InputHook, output_hook: OutputCallBack):
        self.input_hook = input_hook
        self.output_hook = output_hook

    def _ask_service_name(self, default=None):
        # TODO (chiragjn): Add validation
        param = Parameter(
            prompt="Name your service (min 5 characters)", default=default
        )
        service_name = self.input_hook.ask_string(param)
        return service_name

    def _ask_workspace(self, default=None):
        prompt = "Choose a workspace to deploy your service"
        if default:
            # TODO (chiragjn): Add default option for asking workspace
            raise NotImplementedError
        workspace_fqn = self.input_hook.ask_workspace(WorkspaceParameter(prompt=prompt))
        return workspace_fqn

    def _ask_cpu_required(self, default=0.5):
        prompt = "Minimum amount of CPU to allocate (1 = 1 physical/virtual core, min 0.0001)"
        # TODO (chiragjn): Add validation
        cpu_required = self.input_hook.ask_float(
            Parameter(prompt=prompt, default=default)
        )
        return CPU(required=cpu_required, limit=None)

    def _ask_memory_required(self, default=128):
        prompt = "Minimum amount of memory to allocate (in MB, min 1)"
        # TODO (chiragjn): Add validation
        mem_required = (
            self.input_hook.ask_integer(Parameter(prompt=prompt, default=default))
            * 1000
            * 1000
        )
        return Memory(required=mem_required, limit=None)

    def _ask_replicas(self, default=1):
        prompt = "Choose a number of replicas for your service"
        # TODO (chiragjn): Add validation
        replicas = self.input_hook.ask_integer(
            Parameter(prompt=prompt, default=default)
        )
        return replicas

    def _ask_port(self, default=8000):
        prompt = "Choose a port to expose for your service"
        # TODO (chiragjn): support more complex schema like "0.0.0.0:8000:80/TCP"
        # TODO (chiragjn): Add validation
        port = self.input_hook.ask_integer(Parameter(prompt=prompt, default=default))
        return Port(container_port=port)

    def generate(self, default_service_name) -> ServiceFoundryDefinition:
        service_name = self._ask_service_name(default=default_service_name)
        # TODO (chiragjn): create a template out of this that can be put on server and
        #                  shared between UI and CLI.
        cpu_resource = self._ask_cpu_required()
        mem_resource = self._ask_memory_required()
        port = self._ask_port()
        replicas = self._ask_replicas()
        sf_definition = ServiceFoundryDefinition(
            build=None,
            service=ServiceFoundryServiceDefinition(
                name=service_name,
                # TODO (chiragjn): this to_dict is quite redundant, figure out a better way
                cpu=cpu_resource,
                memory=mem_resource,
                ports=[port.to_str()],
                replicas=replicas,
            ),
        )
        return sf_definition

    def fill_missing(
        self, sf_definition: ServiceFoundryDefinition
    ) -> ServiceFoundryDefinition:
        service = sf_definition.service
        if not service.workspace:
            service.workspace = self._ask_workspace()
        if not service.ports:
            service.ports = [self._ask_port()]
        return sf_definition
