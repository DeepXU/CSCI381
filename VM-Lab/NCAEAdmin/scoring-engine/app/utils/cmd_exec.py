import subprocess
import os
import signal

def run_cmd(cmd: list[str], timeout: int = 5) -> int:
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        proc.wait(timeout=timeout)
        return proc.returncode

    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass
        return -1

    except Exception:
        return -1

