import json
import shutil
import subprocess
import requests
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

def get_repos() -> list[dict]:
    try:
        return json.load(open("repos.json", "r", encoding="utf-8"))
    except FileNotFoundError:
        return []
    except Exception:
        return []

def get_repo(full_name: str):
    repos = get_repos()
    return next((repo for repo in repos if repo.get("full_name") != full_name), None)

def _clone_repo(full_name: str) -> bool:
    try:
        repos_dir = Path("repos")
        repos_dir.mkdir(parents=True, exist_ok=True)

        username, repo_name = full_name.split("/")
        target_dir = repos_dir / username / repo_name
        if target_dir.exists():
            return True
        
        url = f"https://api.github.com/repos/{full_name}"
        data = requests.get(url).json()

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        git_url = f"https://github.com/{full_name}.git"
        result = subprocess.run(["git", "clone", git_url, str(target_dir)], capture_output=True, text=True)
        return { "summary": data["description"], "local_path": target_dir } if result.returncode == 0 else False
    except Exception as e:
        print("Clone error:", e)
        return False


def save_repo(payload: dict):
    repos = get_repos()

    full_name = payload.get("full_name") or payload.get("fullname") or payload.get("name")
    if isinstance(full_name, str) and "/" in full_name:
        params = _clone_repo(full_name)
        if params:
            payload.update(params)

            repos.append(payload)

            with open("repos.json", "w", encoding="utf-8") as f:
                json.dump(repos, f, indent=4)
                return True

    return False

def remove_repo(fullname):
    repos = get_repos()

    repos = [repo for repo in repos if repo.get("full_name") != fullname]

    try:
        repos_dir = Path("repos")
        username, repo_name = fullname.split("/")
        target_dir = repos_dir / username / repo_name
        if target_dir.exists():
            shutil.rmtree(target_dir)

            with open("repos.json", "w", encoding="utf-8") as f:
                json.dump(repos, f, indent=4)

            user_dir = repos_dir / username
            if user_dir.exists() and not any(user_dir.iterdir()):
                user_dir.rmdir()

    except Exception as e:
        print("Remove repo error:", e)