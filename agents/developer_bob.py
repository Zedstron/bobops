
from bob import run_bob

ROLE_PROMPTS = {
    "feature_developer": "Implement production-grade features.",
    "bug_fixer": "Fix bugs conservatively with minimal regression risk.",
    "github_issue_investigator": "Investigate issue causes and propose remediation."
}


def developer_bob(state):
    role = state.get("developer_role", "bug_fixer")

    role_instruction = ROLE_PROMPTS.get(role)

    prompt = f"""
    Task: {state.get('task') or ''}

    Role: {role}
    Role Instruction: {role_instruction}

    Inspector Summary:
    {state.get('inspector_summary') or ''}

    Produce:
    1) Code changes (provide diffs or files)
    2) Refactoring recommendations
    3) Deployment considerations
    4) Suggested test cases
    Provide a short PR description at the end.
    """

    output = run_bob("developer", prompt)

    state["code_changes"] = output

    return state
