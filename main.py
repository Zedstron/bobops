
from dotenv import load_dotenv

from graph import app

load_dotenv()

initial_state = {
    "task": "Investigate websocket disconnect issue causing delayed baby monitor alerts.",
    "developer_role": "bug_fixer",

    "invoke_story_bob": True,
    "invoke_qa_bob": True,

    "log_context": '''
    websocket reconnect storm observed
    notification queue timeout
    retry handler loop detected
    memory consumption spike
    '''
}

result = app.invoke(initial_state)

print("\n=== TEAM OF BOBS EXECUTION COMPLETE ===\n")

for key, value in result.items():
    print(f"\n--- {key} ---\n")
    print(value)
