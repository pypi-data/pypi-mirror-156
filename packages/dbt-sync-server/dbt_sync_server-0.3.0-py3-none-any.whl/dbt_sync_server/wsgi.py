import os
from dbt_sync_server import DbtClient, STATE, app, exec_rpc, check_rpc

rpc_port = os.getenv("RPC_PORT", 8580)
project_dir = os.getenv("PROJECT_DIR", "./")
profiles_dir = os.getenv("PROFILES_DIR", "~/.dbt")
profile = os.getenv("PROFILE", "default")
target = os.getenv("TARGET", "dev")

STATE["server"] = DbtClient(port=rpc_port)

exec_rpc(rpc_port, project_dir, profiles_dir, profile, target)
check_rpc()
