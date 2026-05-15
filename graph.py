from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END

from state import TeamOfBobsState

from agents.inspector_bob import inspector_bob
from agents.product_owner_bob import product_owner_bob
from agents.story_bob import story_bob
from agents.memory_bob import (
    memory_retrieve_bob,
    memory_store_bob
)
from agents.architect_bob import architect_bob
from agents.developer_bob import developer_bob
from agents.security_bob import security_bob
from agents.qa_bob import qa_bob
from agents.pr_creator_bob import pr_creator_bob


def should_run_story(state):
    return "story" if state.get("invoke_story_bob") else "memory"


def should_run_qa(state):
    return "qa" if state.get("invoke_qa_bob") else "memory_store"


def should_revise_after_security(state):
    return (
        "developer_revision"
        if not state.get("security_approved")
        else "qa_or_memory"
    )


workflow = StateGraph(TeamOfBobsState)

# Nodes

workflow.add_node("inspector", inspector_bob)

workflow.add_node(
    "product_owner",
    product_owner_bob
)

workflow.add_node(
    "story",
    story_bob
)

workflow.add_node(
    "memory",
    memory_retrieve_bob
)

workflow.add_node(
    "architect",
    architect_bob
)

workflow.add_node(
    "developer",
    developer_bob
)

workflow.add_node(
    "security",
    security_bob
)

workflow.add_node(
    "qa",
    qa_bob
)

workflow.add_node(
    "memory_store",
    memory_store_bob
)

workflow.add_node(
    "pr",
    pr_creator_bob
)

# Entry

workflow.set_entry_point("inspector")

# Flow

workflow.add_edge(
    "inspector",
    "product_owner"
)

workflow.add_conditional_edges(
    "product_owner",
    should_run_story,
    {
        "story": "story",
        "memory": "memory"
    }
)

workflow.add_edge(
    "story",
    "memory"
)

workflow.add_edge(
    "memory",
    "architect"
)

workflow.add_edge(
    "architect",
    "developer"
)

workflow.add_edge(
    "developer",
    "security"
)

workflow.add_conditional_edges(
    "security",
    should_revise_after_security,
    {
        "developer_revision": "developer",
        "qa_or_memory": "qa"
    }
)

workflow.add_conditional_edges(
    "qa",
    should_run_qa,
    {
        "qa": "qa",
        "memory_store": "memory_store"
    }
)

workflow.add_edge(
    "memory_store",
    "pr"
)

workflow.add_edge(
    "pr",
    END
)

app = workflow.compile()

if __name__ == "__main__":
    app.get_graph().draw_mermaid_png(
        output_file_path="docs/workflow.png"
    )

    print("Workflow graph generated at workflow.png")