from dotenv import load_dotenv
load_dotenv()

from graph import app

if __name__ == "__main__":
    app.get_graph().draw_mermaid_png(
        output_file_path="docs/workflow.png"
    )

    print("Workflow graph generated in docs")