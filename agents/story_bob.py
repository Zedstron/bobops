
from bob import run_bob


def story_bob(state):
    prompt = f"""
Task: {state.get('task') or ''}

Inspector Summary:
{state.get('inspector_summary') or ''}

Produce a concise backlog story with title, description, acceptance criteria, and suggested estimate.
"""

    output = run_bob("story", prompt)

    state["story_output"] = output

    return state
