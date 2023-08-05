import logging

import rich_click as click

from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.io.cli_input_hook import CliInputHook
from servicefoundry.cli.io.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.sfy_init.init import init

logger = logging.getLogger(__name__)


@click.command(
    name="init", cls=COMMAND_CLS, help="Initialize a new Service for servicefoundry"
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(exists=False, file_okay=False, writable=True, resolve_path=True),
    default=None,
    help="directory to init in",
)
@handle_exception_wrapper
def init_command(directory):
    client = ServiceFoundryServiceClient.get_client()
    input_hook = CliInputHook(client)
    output_hook = RichOutputCallBack()
    init(directory, input_hook, output_hook)


def get_init_command():
    return init_command
