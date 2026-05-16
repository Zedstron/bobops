from langgraph.graph import StateGraph, END

from state import TeamOfBobsState

from agents.inspector_bob import inspector_bob
from agents.product_owner_bob import product_owner_bob
from agents.story_bob import story_bob
from agents.memory import save_memory, get_memory
from agents.architect_bob import architect_bob
from agents.developer_bob import developer_bob
from agents.security_bob import security_bob
from agents.qa_bob import qa_bob
from agents.pr_creator import pr_creator


def should_run_story(state):
    return "story" if state.get("invoke_story_bob") else "get_memory"

def evaluate_next_node(state):
    if state.get("invoke_security_bob"):
        return "security"
    elif state.get("invoke_qa_bob"):
        return "qa"
    
    return "save_memory"

def should_revise_after_security(state):
    return "developer" if not state.get("security_approved") else "qa"


workflow = StateGraph(TeamOfBobsState)

workflow.add_node("inspector", inspector_bob)
workflow.add_node("product_owner", product_owner_bob)
workflow.add_node("story", story_bob)
workflow.add_node("save_memory", save_memory)
workflow.add_node("get_memory", get_memory)
workflow.add_node("architect", architect_bob)
workflow.add_node("developer", developer_bob)
workflow.add_node("security", security_bob)
workflow.add_node("qa", qa_bob)
workflow.add_node("pr", pr_creator)

workflow.set_entry_point("inspector")

workflow.add_edge("inspector", "product_owner")

workflow.add_conditional_edges(
    "product_owner",
    should_run_story,
    {
        "story": "story",
        "get_memory": "get_memory",
    },
)

workflow.add_edge("story", "get_memory")
workflow.add_edge("get_memory", "architect")
workflow.add_edge("architect", "developer")

workflow.add_conditional_edges(
    "developer",
    evaluate_next_node,
    {
        "security": "security",
        "qa": "qa",
        "save_memory": "save_memory"
    },
)

workflow.add_conditional_edges(
    "security",
    should_revise_after_security,
    {
        "developer": "developer",
        "qa": "qa",
    },
)

workflow.add_edge("qa", "save_memory")
workflow.add_edge("save_memory", "pr")
workflow.add_edge("pr", END)

app = workflow.compile()