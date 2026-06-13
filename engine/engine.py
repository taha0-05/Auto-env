import json
import re
from PyQt6.QtCore import QObject, pyqtSignal
from .scanner import scan_system
from .nlp import parse_prompt
from .resolver import resolve_dependencies
from .graph import build_execution_graph

class Engine(QObject):
    """Core engine orchestrating the workflow.

    Signals:
        graphReady(dict) – emitted when the execution graph is built.
        logMessage(str) – UI can display logs.
    """
    graphReady = pyqtSignal(dict)
    logMessage = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.system_info = None
        self.actions = []

    def process_prompt(self, prompt: str):
        self.logMessage.emit(f"🔍 Received prompt: {prompt}")
        # 1. Scan system
        self.system_info = scan_system()
        self.logMessage.emit("🖥️ System scan completed.")
        # 2. Parse prompt
        parsed = parse_prompt(prompt)
        self.logMessage.emit(f"🧠 Parsed intent: {json.dumps(parsed)}")
        # 3. Resolve dependencies
        self.actions = resolve_dependencies(parsed, self.system_info)
        self.logMessage.emit(f"📦 Resolved {len(self.actions)} actions.")
        # 4. Build execution graph
        graph = build_execution_graph(self.actions)
        self.graphReady.emit(graph)
