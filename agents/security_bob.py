from bob import run_bob

def security_bob(state):
    prompt = f"""
    Generated Code:
    {state.get('code_changes') or ''}

    Acceptance Criteria:
    {state.get('acceptance_criteria') or ''}

    Review for:
    - Injection risks
    - Broken auth/authorization
    - Sensitive data exposure
    - Secrets leakage
    - Unsafe patterns
    - Regression risks

    Produce a prioritized security report, list of vulnerabilities with severity, and concrete remediation steps. Indicate whether the change is a blocker for release.
    """
    keywords = ( "critical", "high severity", "must fix" )

    content = run_bob("security", prompt)

    state["security_report"] = content

    lower = content.lower()

    state["security_approved"] = all([ k not in lower for k in keywords ])

    return state