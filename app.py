from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException, status
from utils.db import save_repo, get_repos, remove_repo, save_incident, get_incidents
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.helpers import find_log_file
from monitor_pool import LogMonitorPool
from sockethandler import SocketManager
from utils.models import *

pool = LogMonitorPool()
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

def new_error_received(detail, repo):
    save_incident(detail, repo)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", { "request": request })

@app.get("/incidents", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("incident.html", { "request": request })

@app.post("/incident/{incident_id}")
async def trigger_fix(incident_id: str):
    return {
        "status": True,
        "message": "The task has been handed over to the Bob"
    }

@app.get("/repo", response_class=HTMLResponse)
async def index(request: Request):
    repos = get_repos()
    for repo in repos:
        repo["monitoring"] = pool.is_running(repo.get("full_name"))

    return templates.TemplateResponse("repo.html", { "request": request, "repos": repos })

@app.put("/repo", status_code=status.HTTP_201_CREATED)
async def add_repo(action: str, repo: Repo):
    if action == "start":
        log_file = find_log_file(repo.name)

        if not log_file:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Cannot start no log file found, make sure the project is running"
            )
        
        if pool.is_running(repo.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A monitor is already running on the repo, Aborting"
            )
        
        pool.start_monitor(repo.name, log_file, new_error_received)
        return { "message": "Successfully started the error monitor on requested repo" }
    
    elif action == "stop":
        if not pool.stop_monitor(repo.name):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops! Technical issue occured while halting monitor, Try again later"
            )
        
        return { "message": "Successfully halted the monitor for the requested repository" }
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid action defined, aborting request"
    )

@app.post("/repo", status_code=status.HTTP_201_CREATED)
async def add_repo(repo: Repo):
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
        "summary": "",
        "status": "active"
    }
    
    if save_repo(new_repo):
        return {
            "success": True,
            "message": f"Repository {repo_name} connected",
            "repo": new_repo
        }
    
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Error Occured while clonning the repository try again later"
    )

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

@app.websocket("/incidents/ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_manager.connect(websocket)

    try:
        for incident in get_incidents():
            await websocket.send_json(incident)

        while True:
            data = await websocket.receive_text()
            await socket_manager.broadcast(data)
    except WebSocketDisconnect:
        socket_manager.disconnect(websocket)