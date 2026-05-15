from bob import run_bob

def architect_bob(state):
    prompt = f"""
    Product Requirements:
    {state.get('product_requirements') or ''}

    Inspector Summary:
    {state.get('inspector_summary') or ''}

    Similar Past Solutions:
    {state.get('memory_matches') or ''}

    Analyze the system and propose a remediation and implementation strategy to address the incident.
    Produce:
    1) Architectural analysis
    2) Affected modules/services
    3) Dependency and deployment considerations
    4) Refactoring or migration suggestions
    5) Recommended implementation approach and rollout plan
    """

    output = run_bob("architect", prompt)

    state["architecture_plan"] = output

    return state