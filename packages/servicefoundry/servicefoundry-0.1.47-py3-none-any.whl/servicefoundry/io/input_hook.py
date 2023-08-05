from abc import ABC, abstractmethod

from servicefoundry.io.parameters import OptionsParameter, Parameter, WorkspaceParameter
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)


class InputHook(ABC):
    def __init__(self, tfs_client: ServiceFoundryServiceClient):
        self.tfs_client = tfs_client

    def get_workspace_choices(self):
        workspaces = self.tfs_client.list_workspace()
        workspaces_choices = [
            (workspace["name"], workspace["fqn"])
            for workspace in workspaces
            if workspace["status"] == "CREATE_SPACE_SUCCEEDED"
        ]
        return workspaces_choices

    @abstractmethod
    def confirm(self, prompt, default=False):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_boolean"
        )

    @abstractmethod
    def ask_string(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_string"
        )

    @abstractmethod
    def ask_number(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_number"
        )

    def ask_integer(self, param: Parameter):
        return self.ask_number(param)

    def ask_float(self, param: Parameter):
        return self.ask_number(param)

    @abstractmethod
    def ask_file_path(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_number"
        )

    @abstractmethod
    def ask_option(self, param: OptionsParameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_option"
        )

    @abstractmethod
    def ask_workspace(self, param: WorkspaceParameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_workspace"
        )

    @abstractmethod
    def ask_python_file(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_file"
        )
