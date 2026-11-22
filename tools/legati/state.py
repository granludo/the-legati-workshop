"""Host-local read markers inside the workspace (.legati-state/, gitignored). Writes are atomic."""
import os
from pathlib import Path
import sys
import tempfile


def atomic_write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".marker-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(value)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def marker_path(repo, name):
    if Path(name).name != name or name in (".", ".."):
        raise ValueError("marker name must be a filename")
    directory = Path(repo) / ".legati-state"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / name


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "path":
        print(marker_path(sys.argv[2], sys.argv[3]))
    elif len(sys.argv) == 3 and sys.argv[1] == "write":
        atomic_write(sys.argv[2], sys.stdin.read())
    else:
        raise SystemExit("usage: state.py path REPO NAME | write PATH")
