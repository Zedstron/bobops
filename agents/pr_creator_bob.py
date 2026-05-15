
import os
from github import Github
from datetime import datetime

def pr_creator_bob(state):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = state["branch_name"]

    github = Github(token)
    repo = github.get_repo(repo_name)

    branch_name = f"team-of-bobs-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    base_branch = repo.default_branch
    source = repo.get_branch(base_branch)

    repo.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=source.commit.sha
    )

    pr = repo.create_pull(
        title=f"[Team of Bobs] {state.get('task')}",
        body=f'''
        ## Inspector Summary

        {state.get("inspector_summary")}

        ## Generated Changes

        {state.get("code_changes")}

        ## QA Report

        {state.get("qa_report")}
        '''.strip(),
            head=branch_name,
            base=base_branch
    )

    state["branch_name"] = branch_name
    state["pr_url"] = pr.html_url

    return state
