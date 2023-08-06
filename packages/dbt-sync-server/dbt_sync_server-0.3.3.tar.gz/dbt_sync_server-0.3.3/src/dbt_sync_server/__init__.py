"""
A super lightweight abstraction of the dbt rpc which serves out synchronous requests
and affords more customization. Should also afford us the ability to swap the RPC
with another solution like `dbt.lib` which dbt server may implicitly use.
"""
import multiprocessing
import subprocess
import time
import os
from typing import Dict
from pathlib import Path

import click
from flask import Flask, request

from .dbt_rpc_client import DbtClient, RPCError

app = Flask(__name__)
__version__ = "0.2.6"

STATE: Dict[str, DbtClient] = {}

LOG_MSG = """
{action} QUERY
===============
{query}
"""


@app.route("/run", methods=["POST"])
def run_sql():
    # Server Logging
    print(LOG_MSG.format(action="RUNNING", query=request.data))
    try:
        # TODO: Lets consider memoization, also make the limit parameterizable
        result = STATE["server"].run_sql(
            "dbt-sync-server",
            f'SELECT * FROM ({request.data.decode("UTF-8")}) AS __rpc_query LIMIT 200',
            sync=True,
        )
    except RPCError as rpc_err:
        return rpc_err.response
    else:
        return {
            **result["result"]["results"][0]["table"],
            "compiled_sql": result["result"]["results"][0]["compiled_sql"],
            "raw_sql": result["result"]["results"][0]["raw_sql"],
        }


@app.route("/compile", methods=["POST"])
def compile_sql():
    # Server Logging
    print(LOG_MSG.format(action="COMPILING", query=request.data))
    try:
        # Lets consider memoization
        result = STATE["server"].compile_sql(
            "dbt-sync-server", request.data.decode("UTF-8"), sync=True
        )
    except RPCError as rpc_err:
        return rpc_err.response
    else:
        return {"result": result["result"]["results"][0]["compiled_sql"]}


@app.route("/api/health", methods=["GET"])
def health_check(raise_on_error: bool = False) -> Dict[str, str]:
    """Example response
    {
    "result": {
        "status": "ready",
        "error": null,
        "logs": [..],
        "timestamp": "2019-10-07T16:30:09.875534Z",
        "pid": 76715
    },
    "id": "2db9a2fe-9a39-41ef-828c-25e04dd6b07d",
    "jsonrpc": "2.0"
    }"""
    try:
        result = STATE["server"].status()
    except RPCError as rpc_err:
        if raise_on_error:
            raise ConnectionError from rpc_err
        return rpc_err.response
    except Exception as exc:
        # Catch alternate errors
        if raise_on_error:
            raise ConnectionError from exc
        return {"error": f"Unknown error has occured: {str(exc)}"}
    else:
        return result


def run_rpc(
    rpc_port: int,
    project_dir: str,
    profiles_dir: str,
    profile: str = None,
    target: str = None,
):
    print(
        f"Starting RPC port:{rpc_port} project_dir:{project_dir} profiles_dir:{profiles_dir} profile:{profile} target:{target}"
    )  # noqa
    try:
        log_filename = os.getenv("DBT_RPC_LOG_FILENAME", "./dbt_rpc.log")

        log_file = Path(log_filename)

        with log_file.open("w") as f:
            args = [
                "dbt-rpc",
                "serve",
                "--port",
                str(rpc_port),
                "--project-dir",
                str(project_dir),
                "--profiles-dir",
                str(profiles_dir),
            ]
            if profile:
                args += [
                    "--profile",
                    str(profile),
                ]
            if target:
                args += [
                    "--target",
                    str(target),
                ]

            subprocess.run(args, stdout=f, stderr=subprocess.STDOUT)
    except Exception as err:
        print(f"RPC Terminated? Error: {err}")


@click.group()
@click.version_option(__version__)
def cli():
    pass


@cli.command()
@click.option("--port", type=click.INT, default=8581)
@click.option("--rpc-port", type=click.INT, default=8580)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default="./",
)
@click.option(
    "--profiles-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default="~/.dbt",
)
@click.option("--profile", type=click.STRING)
@click.option("--target", type=click.STRING)
@click.option("--no-inject-rpc", is_flag=True, type=click.BOOL, default=False)
def serve(
    port: int = 8581,
    rpc_port: int = 8580,
    project_dir: str = "./",
    profiles_dir: str = "~/.dbt",
    profile: str = None,
    target: str = None,
    no_inject_rpc: bool = False,
):
    STATE["server"] = DbtClient(port=rpc_port)
    if not no_inject_rpc:
        try:
            rpc_server = exec_rpc(rpc_port, project_dir, profiles_dir, profile, target)
        except Exception as e:
            print(e)
            exit(1)
    try:
        check_rpc()
        app.run("localhost", port)
    finally:
        print("\nSHUTDOWN")
        if not no_inject_rpc and rpc_server.is_alive():
            print("CLEANING UP RPC")
            rpc_server.terminate()
            rpc_server.join()
            rpc_server.close()


def exec_rpc(
    port: int = 8580,
    project_dir: str = "./",
    profiles_dir: str = "~/.dbt",
    profile: str = None,
    target: str = None,
    wait_time: float = 2.5,
):
    rpc_server = multiprocessing.Process(
        target=run_rpc,
        args=(port, project_dir, profiles_dir, profile, target),
        daemon=True,
    )
    rpc_server.start()
    time.sleep(wait_time)
    if not rpc_server.is_alive():
        exit_code = rpc_server.exitcode
        rpc_server.close()
        error = False
        if exit_code == 0:
            error = f"RPC failed to initialize, exit code {exit_code} most likely indicates a process "
            "is already running on port {port} or the project directory provided [{project_dir}] is not a valid dbt project."
        elif exit_code == 1:
            error = f"RPC failed to initialize, exit code {exit_code} most likely indicates the dbt project is invalid or has an error."
        else:
            error = f"RPC failed to initialize, exit code {exit_code} with unknown root cause."

        if error:
            raise Exception(error)
    return rpc_server


def check_rpc(wait_time: float = 2.5):
    # ping RPC to gaurantee connectivity before starting flask app
    ping_count = 0
    while ping_count < 3:
        if not health_check().get("error"):
            print("RPC health check passed!")
            break
        ping_count += 1
        time.sleep(wait_time)
    else:
        print("RPC health check failing, final attempt")
        health_check(raise_on_error=True)


@cli.command()
def build_shell_scripts():
    """Build shell scripts in local directory. These handle spinning up the server and
    setting up a cron job which will reparse dbt project as needed. Invoke the from the
    main dbt project directory. It includes a kill server script too which will clean up both the
    RPC and the wrapper."""
    # run_server = Path(__file__).parent.parent.parent / "bin" / "run_server.sh"
    # kill_server = Path(__file__).parent.parent.parent / "bin" / "kill_server.sh"
    from textwrap import dedent

    with open("./kill_server.sh", "w") as run_server_target:
        run_server_target.write(
            dedent(
                """
            #!/bin/bash

            # RUN SERVER
            dbt-sync-server serve > dbt_sync.log 2>&1 &

            # CAPTURE PIDs
            echo $! >/tmp/dbt_sync_server.pid
            sleep 2.5
            ps aux | grep dbt-rpc | grep -v grep | awk '{print $2}' >/tmp/dbt_rpc_server.pid

            # SET CRON VARS
            dbt_rpc_id=`cat /tmp/dbt_rpc_server.pid`
            every_x_minutes=5

            # REPARSE DBT PROJECT EVERY X MINUTES
            crontab -l | grep -v '__dbt reparsed__' | crontab
            (crontab -l ; echo "1/$every_x_minutes * * * * kill -HUP $dbt_rpc_id ; echo '__dbt reparsed__'") | crontab

            # USE THIS /tmp/dbt_rpc_server.pid TO REPARSE MANUALLY
            echo $dbt_rpc_id

        """
            )
        )
    with open("./run_server.sh", "w") as kill_server_target:
        kill_server_target.write(
            dedent(
                """
            #!/bin/bash

            # SET VARS
            dbt_rpc_id=`cat /tmp/dbt_rpc_server.pid`
            dbt_ss_id=`cat /tmp/dbt_sync_server.pid`

            # REPARSE DBT PROJECT EVERY X MINUTES
            crontab -l | grep -v '__dbt reparsed__' | crontab
            kill $dbt_rpc_id ; kill $dbt_ss_id

        """
            )
        )


if __name__ == "__main__":
    cli()
