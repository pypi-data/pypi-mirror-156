"""
CLI for Lemmings
"""

import os

import click

from lemmings.cli_main import add_version


@click.group()
@add_version
def main_cli():
    """
    *Lemmings workflow CLI*
    """
    pass

@click.command()
@click.argument("workflow", type=str, nargs=1)
@click.option(
    "--status",
    "-s",
    type=str,
    default="start",
    help="Your job status, Expert users only",
)
@click.option(
    "--inputfile",
    required=False,
    type=str,
    default=None,
    help="Path to .yml file associated with workflow",
)
@click.option(
    "--job-prefix",
    required=False,
    type=str,
    default="lemjob",
    help="Job prefix to be used in chain name.",
)
@click.option(
    "--machine-file",
    required=False,
    type=str,
    default=None,
    help="Allows user specification of  path to {machine}.yml file. "
    + "This will totally override your machine file  $LEMMINGS_MACHINE",
)

def run(
    workflow, status, inputfile, job_prefix, machine_file,
):
    """
    This is the command to launch your workflow with Lemmings.
    ' lemmings run {workflow_name} '
    """
    import logging
    from lemmings.cli_main import main_run, disclaimer
    from lemmings.chain.lemmingsstop import LemmingsStop

    try:
        lemmings = main_run(workflow, inputfile, machine_file,job_prefix ,status)
        if status == "start":
            print(disclaimer())
        lemmings.run()
    except LemmingsStop as exp:
        logging.info(exp)
    except Exception as exp:
        logging.warning(exp)
main_cli.add_command(run)


@click.command()
@click.option(
    "--machine-file",
    required=False,
    type=str,
    default=None,
    help="Allows user specification of  path to {machine}.yml file. "
    + "This will totally override your machine file  $LEMMINGS_MACHINE",
)
def kill(machine_file):
    """
    Kill the current job and pjob of lemmings
    """
    from lemmings.base.database import Database
    from lemmings.cli_main import kill_chain

    if not os.path.isfile("database.json"):
        print("ERROR: Can't use this command")
        print("       no database.json file in the current directory.")
        return
    database = Database()
    # First check that we are in the correct directory to launch this command
    try:
        (par_dict,) = database.get_current_loop_val("parallel_runs")
        print("ERROR: this command can't be called from this directory")
        print("       Try 'lemmings-farming kill' instead")
        return
    except KeyError:
        # we are indeed in a normal lemmings chain
        pass

    kill_chain(machine_file)
main_cli.add_command(kill)


@click.command()
@click.option(
    "--database",
    "-db",
    required=False,
    type=str,
    default=None,
    help="Path to database.json file to read",
)
@click.option(
    "--progress",
    "-p",
    is_flag=True,
    help="If activated, the latest progress will also be shown.",
)
def status(database, progress):
    """
    Show the status during runtime
    """
    from lemmings.base.database import Database
    from lemmings.cli_status import get_current_status

    try:
        if database is not None:
            if os.path.isdir(database):  # try find database.json in directory
                database = os.path.join(database, "database.json")
            if not os.path.isfile(database):
                raise FileNotFoundError(database + " does not exist")
        else:
            if not os.path.isfile("database.json"):
                raise FileNotFoundError("database.json does not exist")
    except FileNotFoundError as excep:
        print("Error: ", excep)
        return

    if database is not None:
        db = Database(database)
    else:
        ## this init will generate a database.json file,
        ## so if not present we should check before
        db = Database()

    # First check that we are in the correct directory to launch this command
    try:
        (par_dict,) = db.get_current_loop_val("parallel_runs")
        print("ERROR: this command can't be called from this directory")
        print("       Try 'lemmings-farming status' instead")
        return
    except KeyError:
        pass

    try:
        # TODO: split get_current_status in two function calls -> farming and normal
        _ = [print(string) for string in get_current_status(db,with_progress=progress)]
    except ValueError as excep:
        print("ValueError:", excep)
        return
    except TypeError as excep:
        print("Database currently not accessible, try again shortly")
        print("Make sure it is not corrupted")
        return  # might be that database chain not found instead!!!
    except KeyError as excep:
        print("Database currently not accessible, try again shortly")
        return
main_cli.add_command(status)


@click.command()
@click.option(
    "--database",
    "-db",
    required=False,
    type=str,
    default=None,
    help="Path to database  YAML file to read",
)
def clean(database):
    """
    Clean lemmings run files in current folder
    """
    from lemmings.cli_main import (
        remove_files_folders,
        gather_default_files_folders_to_clean,
    )

    # need to add option to have other database.json name to look at
    # cfr. lemmings status of FEATURE/parallel branch

    try:
        lst_remove = gather_default_files_folders_to_clean(database)
    except FileNotFoundError as excep:
        print("Error: ", excep)
        return
    except KeyError as excep:
        print(excep)
        if "use lemmings-farming clean" in str(excep):
            return
    for path in lst_remove:
        remove_files_folders(path)


main_cli.add_command(clean)
