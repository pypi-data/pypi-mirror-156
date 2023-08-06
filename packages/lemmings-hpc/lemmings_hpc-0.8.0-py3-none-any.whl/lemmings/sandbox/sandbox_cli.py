"""
CLI for Lemmings
"""

import os
import click
from lemmings.cli_main import add_version

from lemmings.sandbox.sandbox import start_sandbox, submit_sandbox, qstat_sandbox,acct_sandbox, cancel_sandbox


def _default_db_file():
    return os.environ['HOME']+"/"+"sandbox_lem_ddb.json"


@click.group()
@add_version
def sandbox_cli():
    """
    CLI of lemming sandbox to emulate a job scheduler
    """
    pass

@click.command()
@click.option(
    "--db_file",
    type=str,
    default= _default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.option(
    "--frequency",
    "-f",
    type=float,
    default=3,
    help="Demon frequency, in seconds",
)
@click.option(
    "--max_duration",
    "-d",
    type=int,
    default=9,
    help="Demon duration, in seconds",
)
@click.option(
    "--max_jobs",
    "-m",
    type=int,
    default=2,
    help="Maximum of simultaneous jobs",
)

def start(db_file, frequency, max_duration, max_jobs):
    """start the sandbox"""
    start_sandbox(db_file=db_file, frequency=frequency, max_duration=max_duration, max_parallel_jobs=max_jobs)

sandbox_cli.add_command(start)


@click.command()
@click.option(
    "--db_file",
    type=str,
    default= _default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.option(
    "--after",
    "-a",
    type=str,
    default="no",
    help="PID conditioning the start of this run",
)
@click.argument("batchfile", type=str, nargs=1)

def submit(batchfile, db_file, after):
    """Job submission"""
    if after == "no":
        after=None
    pid=submit_sandbox(batchfile, db_file=db_file,after=after)
    print(f"Job submitted with PID {pid}")

sandbox_cli.add_command(submit)

@click.command()
@click.option(
    "--db_file",
    type=str,
    default= _default_db_file(),
    help="Where to store sandbox file ddb",
)
def qstat(db_file):
    """Show queuing state"""
    qstat_sandbox(db_file)

sandbox_cli.add_command(qstat)

@click.command()
@click.option(
    "--db_file",
    type=str,
    default= _default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.argument("pid", type=str, nargs=1)
def cancel(pid, db_file):
    """Cancel job"""
    out = cancel_sandbox(pid, db_file=db_file)
    print(out)

sandbox_cli.add_command(cancel)

@click.command()
@click.option(
    "--db_file",
    type=str,
    default= _default_db_file(),
    help="Where to store sandbox file ddb",
)
@click.argument("pid", type=str, nargs=1)
def acct(pid, db_file):
    """Show accounting in seconds elapsed"""
    print(acct_sandbox(pid, db_file=db_file))
sandbox_cli.add_command(acct)