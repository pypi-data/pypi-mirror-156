import os
from pathlib import Path

from servicefoundry.lib.const import SERVICE_DEF_FILE_NAME
from servicefoundry.lib.exceptions import ConfigurationException
from servicefoundry.service_definition.definition import ServiceFoundryDefinition
from servicefoundry.sfy_build.const import BUILD_DIR
from servicefoundry.utils.file_utils import make_tarfile


def deploy(directory, tf_client):
    if not os.path.isfile(SERVICE_DEF_FILE_NAME):
        raise ConfigurationException(f"Couldn't find {SERVICE_DEF_FILE_NAME}.")
    sfy_yaml = ServiceFoundryDefinition.from_yaml(SERVICE_DEF_FILE_NAME)
    service_def = sfy_yaml.to_service_def()
    build_dir = Path(BUILD_DIR)
    build_dir.mkdir(parents=True, exist_ok=True)
    package_zip = build_dir / "build.tar.gz"
    make_tarfile(package_zip, directory, ignore_list=[BUILD_DIR])
    deployment = tf_client.build_and_deploy(service_def, package_zip)
    return deployment
