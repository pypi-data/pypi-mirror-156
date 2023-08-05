from functools import cache
from pprint import pformat

import docker
import sqlalchemy as sa
from docker.models.containers import Container

from .tables import (
    container_config_table,
    container_env_table,
    container_ulimits_table,
    container_volumes_table,
)
from .utils import get_engine, logger


@cache
def get_docker_client():
    return docker.DockerClient(base_url="unix:///var/run/docker.sock")


def remove_docker_container(task_name: str, warn_on_error: bool = True):
    try:
        get_docker_client().containers.get(task_name).remove()
        logger.info(f"Removed existing container: {task_name}")
    except docker.errors.NotFound:
        if warn_on_error:
            logger.error(
                f"Could not remove docker container '{task_name}'. Container not found."
            )


def _data_columns(table: sa.Table):
    return [c for c in table.columns if c.name != "task_name"]


def create_container_from_db(task_name: str) -> Container:
    """Use configuration stored in the database to create a Docker container for running a script.

    Args:
        task_name (str): Name of task container should be created for.

    Returns:
        Container: The created container.
    """
    # remove any existing container with this name.
    remove_docker_container(task_name, warn_on_error=False)
    # get container info from the database.
    with get_engine().begin() as conn:
        # load configuration.
        container_cfg = conn.execute(
            sa.select(_data_columns(container_config_table)).where(
                container_config_table.c.task_name == task_name
            )
        ).fetchone()
        if not container_cfg:
            raise ValueError(
                f"No container named '{task_name}' found in table '{container_config_table.name}'"
            )
        container_cfg = {k: v for k, v in container_cfg.items() if v is not None}
        if " " in (command := container_cfg["command"]):
            command = command.split()
        # load environment.
        container_env = conn.execute(
            sa.select(
                container_env_table.c.variable,
                container_env_table.c.value
                # variables with 'default' name are applied everything.
            ).where(container_env_table.c.task_name.in_(["default", task_name]))
        ).fetchall()
        if container_env:
            container_cfg["environment"] = dict(container_env)
        # load volumes.
        container_volumes = conn.execute(
            sa.select(
                container_volumes_table.c.host_path,
                container_volumes_table.c.container_path,
                container_volumes_table.c.read_only,
            ).where(container_volumes_table.c.task_name == task_name)
        ).fetchall()
        if container_volumes:
            container_cfg["volumes"] = {
                host_path: {
                    "bind": container_path,
                    "mode": "ro" if read_only else "rw",
                }
                for host_path, container_path, read_only in container_volumes
            }
        # load ulimits.
        container_ulimits = conn.execute(
            sa.select(
                container_ulimits_table.c.name,
                container_ulimits_table.c.soft,
                container_ulimits_table.c.hard,
            ).where(container_ulimits_table.c.task_name == task_name)
        ).fetchall()
        if container_ulimits:
            container_cfg["ulimits"] = [
                docker.types.Ulimit(name=name, soft=soft, hard=hard)
                for name, soft, hard in container_ulimits
            ]
    container_cfg["detach"] = True
    logger.info(f"Creating Docker container for {task_name}:\n{pformat(container_cfg)}")
    return get_docker_client().containers.create(**container_cfg)
