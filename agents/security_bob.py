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

    content = run_bob("security", prompt)

    state["security_report"] = content

    lower = content.lower()

    state["security_approved"] = (
        "critical" not in lower
        and "high severity" not in lower
        and "must fix" not in lower
    )

    return state