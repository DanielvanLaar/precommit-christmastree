import sys
from pathlib import Path
import subprocess


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "tools" / "check_import_length_order.py"

    cmd = [sys.executable, str(script), *sys.argv[1:]]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
