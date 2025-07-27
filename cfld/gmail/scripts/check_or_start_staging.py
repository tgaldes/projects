#!/usr/bin/env python3

import subprocess
import os

# Configuration
WORKING_DIR = "/home/tgaldes/git/projects/cfld/gmail"
LOGFILE = os.path.join(WORKING_DIR, "staging.log")
VENV_ACTIVATE = "/home/tgaldes/git/3rdparty/browser-use/env/bin/activate"
RUN_SCRIPT = "./scripts/run_local_staging.sh"
PROCESS_IDENTIFIER = "main.py orgs/cfld/staging_config.json"

def is_running():
    result = subprocess.run(["pgrep", "-f", PROCESS_IDENTIFIER], stdout=subprocess.PIPE)
    return result.returncode == 0

def start_process():
    command = (
        f'bash -c "source {VENV_ACTIVATE} && {RUN_SCRIPT}"'
    )

    with open(LOGFILE, "ab") as f:
        subprocess.Popen(
            f"nohup {command} >> {LOGFILE} 2>&1 &",
            shell=True,
            cwd=WORKING_DIR,
            stdout=f,
            stderr=subprocess.STDOUT,
            executable="/bin/bash"
        )

def main():
    if is_running():
        print("Staging process is already running.")
    else:
        print("Staging process not running. Starting it...")
        start_process()
        print(f"Started process using {RUN_SCRIPT} in virtual environment.")
        print(f"Logs are being written to: {LOGFILE}")

if __name__ == "__main__":
    main()
