from bob import run_bob


def inspector_bob(state):
    prompt = f"""
    Log/Error Context:
    {state.get('log_context') or ''}

    Please analyze the production incident, form a root-cause hypothesis, and produce a concise technical summary for developers along with immediate mitigation steps.
    """

    output = run_bob("inspector", prompt)

    state["inspector_summary"] = output

    state["acceptance_criteria"] = [
        "Fix root cause",
        "No regression introduced",
        "Tests added",
        "Deployment-safe changes"
    ]

    return state
