from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, status
from utils.helpers import save_repo, get_repos, remove_repo
from pydantic import BaseModel, field_validator, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sockethandler import SocketManager
import re

class RepoCreate(BaseModel):
    name: str = Field(..., example="username/reponame")
    
    @field_validator('name')
    def validate_github_format(cls, v):
        v = v.strip().replace('https://github.com/', '').replace('http://github.com/', '')
        if not re.match(r'^[\w\-\.]+/[\w\-\.]+$', v):
            raise ValueError('Must be GitHub format: username/reponame')
        return v

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", { "request": request })

@app.get("/repo", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("repo.html", { "request": request, "repos": get_repos() })

@app.post("/repo", status_code=status.HTTP_201_CREATED)
async def add_repo(repo: RepoCreate):
    repo_name = repo.name.strip().replace('https://github.com/', '').replace('http://github.com/', '')

    if any(r['full_name'] == repo_name for r in get_repos()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Repository already connected"
        )

    try:
        username, name = repo_name.split('/')
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid repository format"
        )
    
    new_repo = {
        "username": username,
        "name": name,
        "full_name": repo_name,
        "summary": f"Autonomous monitoring enabled • AI-powered incident resolution",
        "status": "active"
    }
    
    save_repo(new_repo)
    
    return {
        "success": True,
        "message": f"Repository {repo_name} connected",
        "repo": new_repo
    }

@app.delete("/repo", status_code=status.HTTP_200_OK)
async def delete_repo(repo_name: str):
    initial_len = len(get_repos())

    remove_repo(repo_name)

    if len(get_repos()) == initial_len:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )

    return {"success": True, "message": f"Removed {repo_name}"}

socket_manager = SocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await socket_manager.broadcast(data)
    except WebSocketDisconnect:
        socket_manager.disconnect(websocket)