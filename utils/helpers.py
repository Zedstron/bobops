import json
import shutil
import subprocess
from pathlib import Path


def get_repos() -> list[dict]:
    try:
        return json.load(open("repos.json", "r", encoding="utf-8"))
    except FileNotFoundError:
        return []
    except Exception:
        return []


def _clone_repo(full_name: str) -> bool:
    try:
        repos_dir = Path("repos")
        repos_dir.mkdir(parents=True, exist_ok=True)

        username, repo_name = full_name.split("/")
        target_dir = repos_dir / username / repo_name
        if target_dir.exists():
            return True

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        git_url = f"https://github.com/{full_name}.git"
        result = subprocess.run(["git", "clone", git_url, str(target_dir)], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print("Clone error:", e)
        return False


def save_repo(payload):
    repos = get_repos()
    repos.append(payload)

    with open("repos.json", "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=4)

    # attempt to clone the repository into repos/<username>/<reponame>
    full_name = payload.get("full_name") or payload.get("fullname") or payload.get("name")
    if isinstance(full_name, str) and "/" in full_name:
        _clone_repo(full_name)


def remove_repo(fullname):
    repos = get_repos()
    # support multiple naming variants
    repos = [repo for repo in repos if repo.get("full_name") != fullname and repo.get("fullname") != fullname and f"{repo.get('username')}/{repo.get('name')}" != fullname]

    with open("repos.json", "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=4)

    # remove filesystem clone if present
    try:
        repos_dir = Path("repos")
        username, repo_name = fullname.split("/")
        target_dir = repos_dir / username / repo_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
            # remove user dir if empty
            user_dir = repos_dir / username
            if user_dir.exists() and not any(user_dir.iterdir()):
                user_dir.rmdir()
    except Exception as e:
        print("Remove repo error:", e)