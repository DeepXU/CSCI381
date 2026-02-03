import subprocess
import logging

def run_cmd(cmd, timeout=6):
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            start_new_session=True
        )
        return result

    except subprocess.TimeoutExpired:
        logging.warning(f"Command timed out: {' '.join(cmd)}")
        return None

