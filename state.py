
from typing import TypedDict, List, Dict, Any

class TeamOfBobsState(TypedDict, total=False):
    task: str
    developer_role: str

    invoke_story_bob: bool
    invoke_qa_bob: bool

    log_context: str
    inspector_summary: str
    acceptance_criteria: List[str]

    story_output: str

    code_changes: str
    generated_tests: str

    qa_report: str

    branch_name: str
    pr_url: str

    repo_path: str

    metadata: Dict[str, Any]
