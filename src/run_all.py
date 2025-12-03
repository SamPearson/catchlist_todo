import os
import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parent

    # Base environment for child processes
    env = os.environ.copy()

    # Ensure project root is on PYTHONPATH (needed by the API)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(project_root), env.get("PYTHONPATH", "")]
    )

    # Commands to run API and webapp
    api_cmd = [sys.executable, "-m", "src.api.api"]
    webapp_cmd = [sys.executable, "-m", "src.webapp.webapp"]

    # Start both as subprocesses
    api_proc = subprocess.Popen(api_cmd, cwd=project_root, env=env)
    webapp_proc = subprocess.Popen(webapp_cmd, cwd=project_root, env=env)

    print("API PID:", api_proc.pid)
    print("Webapp PID:", webapp_proc.pid)
    print("Press Ctrl+C to stop both.")

    try:
        # Wait for either process to exit
        while True:
            api_ret = api_proc.poll()
            webapp_ret = webapp_proc.poll()
            if api_ret is not None or webapp_ret is not None:
                break
    except KeyboardInterrupt:
        print("\nStopping services...")

    # Try to terminate both gracefully
    for proc in (api_proc, webapp_proc):
        if proc.poll() is None:
            proc.terminate()

    # Optional: wait a bit and force kill if still alive
    try:
        api_proc.wait(timeout=5)
    except Exception:
        if api_proc.poll() is None:
            api_proc.kill()

    try:
        webapp_proc.wait(timeout=5)
    except Exception:
        if webapp_proc.poll() is None:
            webapp_proc.kill()

    print("Done.")


if __name__ == "__main__":
    main()