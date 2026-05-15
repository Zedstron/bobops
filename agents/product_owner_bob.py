from bob import run_bob


def product_owner_bob(state):
    prompt = f"""
    Incident Summary:
    {state.get('inspector_summary') or ''}
    
    Translate the technical findings into a business-facing summary, define scope and prioritized implementation tasks, and produce acceptance criteria and success metrics.
    """

    output = run_bob("product_owner", prompt)

    state["product_requirements"] = output

    return state