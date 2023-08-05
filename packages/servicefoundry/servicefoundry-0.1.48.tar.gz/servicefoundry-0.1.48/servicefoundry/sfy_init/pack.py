from abc import ABC, abstractmethod

from servicefoundry.service_definition.definition import (
    CPU,
    Memory,
    Port,
    ServiceFoundryDefinition,
    ServiceFoundryServiceDefinition,
)


class Pack(ABC):
    @abstractmethod
    def get_default_service_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_files(self):
        pass

    def get_default_definition(self) -> ServiceFoundryDefinition:
        return ServiceFoundryDefinition(
            build=None,
            service=ServiceFoundryServiceDefinition(
                name=self.get_default_service_name(),
                cpu=CPU(required=0.05, limit=0.1),
                memory=Memory(required=128000000, limit=512000000),
                ports=[Port(containerPort=8080)],
                replicas=1,
            ),
        )
