import re
from pathlib import Path
from pprint import pformat
from typing import List, Optional, Union

import click
import sqlalchemy as sa
from click.core import Group
from dotenv import dotenv_values
from sqlalchemy.dialects import postgresql
from tqdm import tqdm

from . import tables
from .containers import create_container_from_db, remove_docker_container
from .systemd import (
    SYSTEMD_FILE_PREFIX,
    create_scheduled_service_from_db,
    remove_service,
)
from .tables import SCHEMA_NAME, container_config_table, container_env_table
from .utils import get_engine, logger, systemd_dir


def get_tasks_systemd_files() -> List[Path]:
    """Get all systemd files from existing tasks."""
    return list(systemd_dir.glob(f"{SYSTEMD_FILE_PREFIX}*"))


def get_file_task_name(file: Path):
    """Extract task name from a systemd file."""
    return re.sub(f"^{SYSTEMD_FILE_PREFIX}", "", file.stem)


def get_existing_task_names() -> List[str]:
    """Get names of all tasks that have been created."""
    return [get_file_task_name(f) for f in get_tasks_systemd_files()]


def get_scheduled_names():
    """Get names of all scheduled tasks."""
    with get_engine().begin() as conn:
        scheduled_names = set(
            conn.execute(
                sa.select(tables.timer_options_table.c.task_name.distinct())
            ).scalars()
        )
    return scheduled_names


cli = Group("task-flows", chain=True)


@cli.command(name="check_tables")
def check_tables():
    """Create any tables that do not currently exist in the database."""
    with get_engine().begin() as conn:
        if not conn.dialect.has_schema(conn, schema=SCHEMA_NAME):
            logger.info(f"Creating schema '{SCHEMA_NAME}'")
            conn.execute(sa.schema.CreateSchema(SCHEMA_NAME))
        for table in (
            tables.timer_options_table,
            tables.container_config_table,
            tables.container_env_table,
            tables.container_volumes_table,
            tables.container_ulimits_table,
            tables.task_runs_table,
            tables.task_run_errors_table,
        ):
            logger.info(f"Checking table: {table.name}")
            table.create(conn, checkfirst=True)


@cli.command()
@click.argument("file")
@click.argument("task_names", nargs=-1, required=False)
@click.option("--remove_existing", "-r", is_flag=True)
def load_task_env(
    file: str,
    task_names: Optional[Union[str, List[str]]] = None,
    remove_existing: bool = False,
):
    if not task_names:
        with get_engine().begin() as conn:
            task_names = list(
                conn.execute(
                    sa.select(container_config_table.c.task_name.distinct())
                ).scalars()
            )

    elif isinstance(task_names, str):
        task_names = [task_names]
    if remove_existing:
        with get_engine().begin() as conn:
            conn.execute(
                sa.delete(container_env_table).where(
                    container_env_table.c.task_name.in_(task_names)
                )
            )
    env = dotenv_values(file)
    logger.info(
        f"Loading env for {len(task_names)} tasks:\n{pformat(task_names)}:\n{pformat(env)}"
    )
    values = [
        {"task_name": n, "variable": k, "value": v}
        for n in task_names
        for k, v in env.items()
    ]
    statement = postgresql.insert(container_env_table).values(values)
    statement = statement.on_conflict_do_update(
        index_elements=["task_name", "variable"],
        set_={"value": statement.excluded["value"]},
    )
    with get_engine().begin() as conn:
        conn.execute(statement)


@cli.command()
def clean():
    """Remove files from tasks that have been deleted from the database."""
    scheduled_names = get_scheduled_names()
    for file in get_tasks_systemd_files():
        if (task_name := get_file_task_name(file)) not in scheduled_names:
            logger.info(f"Removing files from deleted task: {task_name}")
            remove_service(file)
            remove_docker_container(task_name)


@cli.command()
@click.argument("task_name")
def create_task(task_name: str):
    """Create (or recreate) a scheduled task using configuration from the database.

    Args:
        name (str): Name of the task, as specified in the database.
    """
    create_container_from_db(task_name)
    create_scheduled_service_from_db(task_name)


@cli.command()
@click.option("--recreate_existing", "-r", is_flag=True)
def create_all_tasks(recreate_existing: bool = False):
    """Create scheduled tasks for all tasks configurations in the database.

    Args:
        recreate_existing (bool, optional): Recreate already existing tasks. Defaults to False.
    """
    names_to_create = get_scheduled_names()
    if not recreate_existing:
        existing_task_names = get_existing_task_names()
        logger.info(
            f"Ignoring {len(existing_task_names)} existing tasks (not recreating)."
        )
        names_to_create.difference_update(existing_task_names)
    logger.info(f"Creating {len(names_to_create)} scheduled task(s).")
    for task_name in tqdm(names_to_create):
        create_task(task_name)
