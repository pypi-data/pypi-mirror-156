import logging

import rich_click as click

from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.lib import logout

logger = logging.getLogger(__name__)


@click.command(name="logout", cls=COMMAND_CLS)
@handle_exception_wrapper
def logout():
    """
    Logout current servicefoundry session
    """
    logout()


def get_logout_command():
    return logout
