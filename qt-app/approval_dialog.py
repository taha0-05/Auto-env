import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
from PyQt6.QtCore import Qt

class ApprovalDialog(QDialog):
    """Simple modal that displays the generated execution graph (JSON).
    For the demo we automatically approve all actions when the user clicks OK.
    """
    def __init__(self, graph_json: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Approve Execution Steps")
        self.resize(700, 500)
        self.setObjectName("card_panel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title_lbl = QLabel("Approve Execution Steps")
        title_lbl.setObjectName("hero_label")
        layout.addWidget(title_lbl)

        # Show the raw JSON – a real product would render a nice graph with checkboxes
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setObjectName("terminal_log")
        # pretty‑print JSON if possible
        try:
            pretty = json.dumps(json.loads(graph_json), indent=2)
        except Exception:
            pretty = graph_json
        self.text_edit.setPlainText(pretty)
        layout.addWidget(self.text_edit)

        # OK / Cancel buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        approve_btn = QPushButton("Approve")
        approve_btn.setObjectName("approve_button")
        approve_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        approve_btn.clicked.connect(self.accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(approve_btn)
        layout.addLayout(btn_layout)

        self._graph = json.loads(graph_json) if isinstance(graph_json, str) else graph_json

    def get_approved_actions(self):
        """Return the list of actions the user approved.
        In this simplified version we return *all* actions if the dialog was accepted.
        """
        if hasattr(self, "_graph") and isinstance(self._graph, dict):
            return self._graph.get("actions", [])
        return []
