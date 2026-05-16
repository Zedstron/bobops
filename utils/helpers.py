from pathlib import Path

LOG_EXTENSIONS = {".log", ".logs", ".txt"}
KEYWORDS = {"log", "error", "debug", "trace" }


def is_log_file(path: Path) -> bool:
    if path.suffix.lower() in LOG_EXTENSIONS:
        return True

    name = path.name.lower()
    return any(k in name for k in KEYWORDS)


def find_log_file(root_dir: str) -> str | None:
    root = Path(root_dir)

    candidates = []

    for path in root.rglob("*"):
        try:
            if path.is_file() and is_log_file(path):
                candidates.append(path)
        except (PermissionError, OSError):
            continue

    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return str(candidates[0])