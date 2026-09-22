"""Shared gate execution and hash-bound provenance for simulation runs."""
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def provenance(inputs=()):
    def git(*args):
        run = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        return run.stdout.strip() if run.returncode == 0 else None

    paths = sorted((ROOT / "src").glob("*.py"))
    paths += [ROOT / "requirements-lock.txt"]
    paths += [ROOT / p for p in inputs]
    return {
        "started_utc": utc_now(), "git_revision": git("rev-parse", "HEAD"),
        "git_status": git("status", "--porcelain"), "python": sys.version,
        "platform": platform.platform(),
        "dependencies": {name: version(name) for name in ("numpy", "scipy", "matplotlib")},
        "threads": {name: os.environ.get(name) for name in
                    ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
        "input_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in paths},
    }


def verify_inputs(manifest):
    changed = [name for name, digest in manifest["input_sha256"].items()
               if not (ROOT / name).is_file() or sha256(ROOT / name) != digest]
    if changed:
        raise RuntimeError("Inputs changed during the run: " + ", ".join(changed))


def run_gate(script):
    """Isolate bootstrap module names and fail before any experiment output write."""
    result = subprocess.run([sys.executable, "-u", str(ROOT / "src" / script)],
                            cwd=ROOT, text=True, capture_output=True)
    print(result.stdout, end="", flush=True)
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr, flush=True)
    if result.returncode:
        raise RuntimeError(f"Gate {script} failed (exit {result.returncode}); run aborted")
    return {"script": script, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}
