import os, subprocess, time, sys
import signal  
import pytest
from pathlib import Path

TEST_PORT = os.getenv("E2E_PORT", "5000") 

PROJECT_ROOT = Path(__file__).resolve().parents[2]

@pytest.fixture(scope="session", autouse=True)
def run_app_server():
    """
    Starts the Flask app on a separate process for E2E tests.
    Here we just run `python app.py` from the project root.
    """
    env = os.environ.copy()
    env["FLASK_ENV"] = "production"
    env["SKIP_SAMPLE_DATA"] = "1" 

    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=PROJECT_ROOT,
    )

    base = f"http://127.0.0.1:{TEST_PORT}"
    ready = False
    for _ in range(60):
        time.sleep(0.5)
        try:
            import urllib.request
            urllib.request.urlopen(base + "/catalog", timeout=0.5)
            ready = True
            break
        except Exception:
            pass

    if not ready:
        proc.kill()
        out = proc.stdout.read().decode("utf-8", errors="ignore") if proc.stdout else ""
        pytest.fail(f"App failed to start on {base}\n{out}")

    yield
    
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
