
import os
from github import Github
from datetime import datetime

def pr_creator(state):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = state["repo_name"]
    story_id = state.get("story_id")

    github = Github(token)
    repo = github.get_repo(repo_name)

    branch_name = f"team-of-bobs-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    if story_id:
        branch_name = f"team-of-bobs-task-{story_id}"

    base_branch = repo.default_branch
    source = repo.get_branch(base_branch)

    repo.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=source.commit.sha
    )

    if not state.get("qa_report"):
        state["qa_report"] = "QA was disabled for this task"
    
    if not state.get("security_report"):
        state["security_report"] = "Security Scanning was disabled for this task"

    pr = repo.create_pull(
        title=f"[Team of Bobs] {state.get('issue')}",
        body=f'''
        ## Initial Logs Analysis & Findings

        {state.get("inspector_summary")}

        ## Generated Changes

        {state.get("code_changes")}

        ## QA Report

        {state.get("qa_report")}

        ## Security & Vulnerability Assessment

        {state.get("security_report")}
        '''.strip(),
            head=branch_name,
            base=base_branch
    )

    state["branch_name"] = branch_name
    state["pr_url"] = pr.html_url

    return state
