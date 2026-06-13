import sys
from pathlib import Path

# Ensure the project root is in sys.path so that engine modules can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from qt_app.prompt_widget import PromptWidget
from qt_app.approval_dialog import ApprovalDialog
from qt_app.graph_view import GraphView

from PyQt6.QtWidgets import QApplication, QStackedWidget


def main():
    app = QApplication(sys.argv)
    # Stacked widget to switch between screens (prompt -> approval -> graph)
    stack = QStackedWidget()

    # Prompt screen
    prompt = PromptWidget()
    stack.addWidget(prompt)

    # Graph view (will be added later)
    graph_view = GraphView()
    stack.addWidget(graph_view)

    # Connect signals
    def on_analyze(prompt_text):
        # Pass prompt text to engine, get graph JSON
        from engine.engine import process_prompt, execute_actions
        graph_json = process_prompt(prompt_text)
        # Show approval dialog
        approval = ApprovalDialog(graph_json)
        if approval.exec():
            approved_actions = approval.get_approved_actions()
            execution_result = execute_actions(approved_actions)
            # Load graph with status updates
            graph_view.load_graph(execution_result)
            stack.setCurrentWidget(graph_view)
        else:
            # User cancelled; stay on prompt screen
            pass
    
    prompt.analyzeRequested.connect(on_analyze)

    stack.setCurrentWidget(prompt)
    stack.resize(900, 650)
    stack.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
