from enum import Enum
from typing import Any, Dict, Union

from pydantic import BaseModel

from servicefoundry.lib.const import KIND
from servicefoundry.lib.exceptions import ConfigurationException

default = Union[str, int, float, None]


class Kind(str, Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = NUMBER
    FLOAT = "float"
    OPTIONS = "options"
    WORKSPACE = "tfy-workspace"
    FILE = "tfy-file"
    PYTHON_FILE = "tfy-python-file"


class Parameter(BaseModel):
    prompt: str
    default: default
    suggest: default


class OptionsParameter(Parameter):
    options: Dict[Any, str]


class WorkspaceParameter(OptionsParameter):
    pass


def get_parameter(parameter: Dict):
    raise RuntimeError("Don't use")
