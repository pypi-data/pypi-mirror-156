import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.io.parameters import OptionsParameter
from servicefoundry.service_definition.definition_generator import (
    ServiceFoundryDefinitionGenerator,
)
from servicefoundry.sfy_init.init_pack import get_init_pack
from servicefoundry.sfy_init.pack import Pack
from servicefoundry.utils.file_utils import create_file_from_content


def _create_directory(directory, output_hook: OutputCallBack):
    if not directory.exists():
        output_hook.print_line(f"Creating directory {directory.resolve()}")
        directory.mkdir(parents=True, exist_ok=True)


def _maybe_backup_file(file_path, input_hook: InputHook, output_hook: OutputCallBack):
    if file_path.exists():
        overwrite = input_hook.confirm(
            prompt=f"File {str(file_path)!r} already exists, Overwrite?",
            default=False,
        )
        if not overwrite:
            raise Exception("Aborted by user!")
        else:
            _now = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
            destination_path = str(
                file_path.parent / f"{file_path.stem}-{_now}-backup.yaml"
            )
            shutil.copy2(
                src=file_path,
                dst=destination_path,
            )
            output_hook.print_line(
                f"Your current config was backed up to {destination_path!r}"
            )


def init(
    directory,
    input_hook: InputHook,
    output_hook: OutputCallBack,
    filename="servicefoundry.yaml",
):
    default_service_name = None
    if directory and os.path.isdir(directory):
        default_service_name = Path(directory).name

    params = OptionsParameter(prompt="Choose a template", options=get_init_pack())
    init_pack: Pack = input_hook.ask_option(params)
    if not default_service_name:
        default_service_name = init_pack.get_default_service_name()

    definition = ServiceFoundryDefinitionGenerator(
        input_hook=input_hook, output_hook=output_hook
    ).generate(default_service_name=default_service_name)

    if not directory:
        directory = definition.service.name
    directory = Path(directory).resolve()
    _create_directory(directory=directory, output_hook=output_hook)

    definition_path = directory / filename
    _maybe_backup_file(
        file_path=definition_path, input_hook=input_hook, output_hook=output_hook
    )
    definition.to_yaml(definition_path)
    output_hook.print_line(f"Created definition file {definition_path.resolve()}")

    _create_init_pack_files(directory, init_pack, input_hook, output_hook)


def _create_init_pack_files(directory, init_pack, input_hook, output_hook):
    files: Dict[str, str] = init_pack.get_files()
    for file, content in files.items():
        file_path = directory / file
        _maybe_backup_file(
            file_path=file_path, input_hook=input_hook, output_hook=output_hook
        )
        create_file_from_content(file_path, content)
        output_hook.print_line(f"Created file {file_path.resolve()}")
