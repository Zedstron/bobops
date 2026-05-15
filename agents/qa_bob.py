from bob import run_bob


def qa_bob(state):
    criteria = "\n".join(state.get("acceptance_criteria", []))

    prompt = f"""
    Acceptance Criteria:
    {criteria}

    Generated Changes:
    {state.get('code_changes') or ''}

    Please produce a QA validation report, list edge cases and regression scenarios, and provide automated test skeletons where applicable.
    """

    output = run_bob("qa", prompt)

    state["qa_report"] = output

    return state
