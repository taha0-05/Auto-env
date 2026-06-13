from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRect

class GraphView(QWidget):
    """Renders a beautiful step-wise horizontal execution graph."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.steps = []
        self._dark = True
        
    def set_blueprint(self, blueprint: dict, dark: bool = True):
        self._dark = dark
        self.steps = []
        
        project_name = blueprint.get("project_name", "my_project")
        self.steps.append(("Initialize", project_name))
        
        structure = blueprint.get("structure", [])
        if structure:
            self.steps.append(("Structure", f"{len(structure)} items"))
            
        stack = blueprint.get("stack", {})
        lang = stack.get("language", "python")
        if lang == "python":
            self.steps.append(("Environment", "Python venv"))
        elif lang in ("node", "javascript", "typescript"):
            self.steps.append(("Environment", "Node / npm"))
            
        deps = blueprint.get("dependencies", [])
        if deps:
            self.steps.append(("Dependencies", f"{len(deps)} packages"))
            
        env_vars = blueprint.get("env_vars", {})
        if env_vars:
            self.steps.append(("Configuration", ".env config"))
            
        self.update()

    def paintEvent(self, event):
        if not self.steps:
            return
            
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = QColor("#00D4FF") if self._dark else QColor("#0066FF")
        text_color = QColor("#E8E8F0") if self._dark else QColor("#1A1A2E")
        sub_color = QColor("#7070A0") if self._dark else QColor("#8090B0")
        line_color = QColor("#3A3A55") if self._dark else QColor("#D0D8E8")
        bg_color = QColor("#16161E") if self._dark else QColor("#FFFFFF")
        
        w = self.width()
        n = len(self.steps)
        
        padding = 60
        available_w = w - 2 * padding
        spacing = available_w / (n - 1) if n > 1 else 0
        
        circle_r = 22
        y_circle = 40
        
        # Draw dashed connecting lines
        if n > 1:
            p.setPen(QPen(line_color, 2, Qt.PenStyle.DashLine))
            p.drawLine(padding, y_circle, w - padding, y_circle)
            
        # Draw step nodes
        for i, (title, sub) in enumerate(self.steps):
            cx = padding + i * spacing
            
            p.setBrush(QBrush(bg_color))
            p.setPen(QPen(color, 2))
            p.drawEllipse(int(cx - circle_r), int(y_circle - circle_r), circle_r*2, circle_r*2)
            
            p.setPen(QPen(color))
            f = p.font()
            f.setBold(True)
            f.setPointSize(12)
            p.setFont(f)
            p.drawText(int(cx - circle_r), int(y_circle - circle_r), circle_r*2, circle_r*2, Qt.AlignmentFlag.AlignCenter, str(i+1))
            
            p.setPen(QPen(text_color))
            f.setPointSize(10)
            p.setFont(f)
            text_rect = QRect(int(cx - 60), int(y_circle + circle_r + 10), 120, 20)
            p.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, title)
            
            p.setPen(QPen(sub_color))
            f.setBold(False)
            f.setPointSize(9)
            p.setFont(f)
            sub_rect = QRect(int(cx - 60), int(y_circle + circle_r + 28), 120, 20)
            p.drawText(sub_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, sub)
