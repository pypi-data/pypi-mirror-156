from abc import ABC, abstractmethod

from servicefoundry.io.parameters import OptionsParameter, Parameter, WorkspaceParameter


class InputHook(ABC):
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
