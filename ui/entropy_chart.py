from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import QRectF

class EntropyChart(QGraphicsView):
    PATTERN_COLORS = {
        'dictionary': QColor("#e74c3c"),
        'repeat': QColor("#f1c40f"),
        'sequence': QColor("#2ecc71"),
        'spatial': QColor("#3498db"),
        'date': QColor("#9b59b6"),
        'regex': QColor("#1abc9c"),
        'bruteforce': QColor("#7f8c8d"),
        'default': QColor("#bdc3c7")
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

    def update_chart(self, password: str, sequence: list[dict]):
        self._scene.clear()
        if not password or not sequence:
            return

        total_length = len(password)
        viewport = self.viewport()
        if viewport is None:
            # fallback (rare case, basically defensive)
            view_width, height = self.width(), self.height()
        else:
            view_width, height = viewport.width(), viewport.height()

        self._scene.setSceneRect(0, 0, view_width, height)

        for match in sequence:
            i, j = match['i'], match['j']
            span = j - i + 1
            x = (i / total_length) * view_width
            w = (span / total_length) * view_width

            rect = QGraphicsRectItem(QRectF(x, 0, w, height))
            pattern = match.get('pattern', 'default')
            color = self.PATTERN_COLORS.get(pattern, self.PATTERN_COLORS['default'])
            rect.setBrush(QBrush(color))
            rect.setToolTip(f"{pattern.capitalize()}: '{match.get('token', '')}'")
            rect.setPen(QColor(0, 0, 0, 30))  # subtle outline
            self._scene.addItem(rect)
