import sqlite3
import subprocess
import requests
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data.db"
REPOS_DIR = ROOT / "repos"

def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _initialize():
    conn = _get_conn()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS repos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                name TEXT NOT NULL,
                full_name TEXT UNIQUE NOT NULL,
                summary TEXT,
                status TEXT,
                local_path TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                repo_full_name TEXT,
                level TEXT,
                title TEXT,
                exception_type TEXT,
                traceback TEXT,
                raw TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    conn.close()


_initialize()


def get_repos() -> List[Dict[str, Any]]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT username, name, full_name, summary, status, local_path FROM repos ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_repo(full_name: str) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT username, name, full_name, summary, status, local_path FROM repos WHERE full_name = ?",
        (full_name,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _clone_repo(full_name: str):
    try:
        REPOS_DIR.mkdir(parents=True, exist_ok=True)

        username, repo_name = full_name.split("/")
        target_dir = REPOS_DIR / username / repo_name
        if target_dir.exists():
            return {"summary": None, "local_path": str(target_dir)}

        url = f"https://api.github.com/repos/{full_name}"
        data = requests.get(url).json()

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        git_url = f"https://github.com/{full_name}.git"
        result = subprocess.run(["git", "clone", git_url, str(target_dir)], capture_output=True, text=True)
        return {"summary": data.get("description"), "local_path": str(target_dir)} if result.returncode == 0 else False
    except Exception as e:
        print("Clone error:", e)
        return False


def save_repo(payload: Dict[str, Any]) -> bool:
    full_name = payload.get("full_name") or payload.get("fullname") or payload.get("name")
    if isinstance(full_name, str) and "/" in full_name:
        params = _clone_repo(full_name)
        if params:
            payload.update(params)

            username, name = full_name.split("/")
            summary = payload.get("summary")
            status = payload.get("status", "active")
            local_path = payload.get("local_path")

            conn = _get_conn()
            try:
                with conn:
                    conn.execute(
                        "INSERT INTO repos (username, name, full_name, summary, status, local_path) VALUES (?, ?, ?, ?, ?, ?)",
                        (username, name, full_name, summary, status, local_path),
                    )
            except Exception as e:
                print("DB insert error:", e)
                conn.close()
                return False

            conn.close()
            return True

    return False


def remove_repo(fullname: str):
    conn = _get_conn()
    with conn:
        conn.execute("DELETE FROM repos WHERE full_name = ?", (fullname,))
    conn.close()

    try:
        repos_dir = REPOS_DIR
        username, repo_name = fullname.split("/")
        target_dir = repos_dir / username / repo_name
        if target_dir.exists():
            shutil.rmtree(target_dir)

            user_dir = repos_dir / username
            if user_dir.exists() and not any(user_dir.iterdir()):
                user_dir.rmdir()

    except Exception as e:
        print("Remove repo error:", e)


def save_incident(event: Any, repo_full_name: Optional[str] = None) -> bool:
    if hasattr(event, "__dict__"):
        data = event.__dict__
    elif isinstance(event, dict):
        data = event
    else:
        return False

    id_ = data.get("id")
    if not id_:
        return False

    level = data.get("level")
    title = data.get("title")
    exception_type = data.get("exception_type")
    traceback = data.get("traceback")
    raw = data.get("raw")
    status = data.get("status")

    conn = _get_conn()
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO incidents (id, repo_full_name, level, title, exception_type, traceback, raw, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (id_, repo_full_name, level, title, exception_type, traceback, raw, status),
        )
    conn.close()
    return True


def get_incidents(repo_full_name: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_conn()
    if repo_full_name:
        rows = conn.execute(
            "SELECT * FROM incidents WHERE repo_full_name = ? ORDER BY created_at DESC", (repo_full_name,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM incidents ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_incident(id_: str) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (id_,)).fetchone()
    conn.close()
    return dict(row) if row else None


def remove_incident(id_: str) -> bool:
    conn = _get_conn()
    with conn:
        conn.execute("DELETE FROM incidents WHERE id = ?", (id_,))
    conn.close()
    return True