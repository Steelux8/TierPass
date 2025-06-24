from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtGui import QColor, QBrush, QPen, QFont
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
            
            token = match.get('token', '')
            pattern = match.get('pattern', 'default')
            guesses_log10 = match.get('guesses_log10', 0)
            entropy_bits = round(guesses_log10 * 3.32, 1)

            tooltip = (
                f"{pattern.capitalize()}: '{token}'\n"
                f"Estimated entropy: ~{entropy_bits} bits"
            )
            rect.setToolTip(tooltip)

            # Add the text label (token) centered on the rectangle
            text_label = f"{token} ({entropy_bits:.0f}b)"
            text_item = QGraphicsTextItem(text_label)
            font = QFont("Arial", 8)
            text_item.setFont(font)

            text_rect = text_item.boundingRect()
            text_x = x + (w - text_rect.width()) / 2
            text_y = (height - text_rect.height()) / 2
            text_item.setPos(text_x, text_y)

            # Optional: ensure text is readable by setting z-order and text color
            text_item.setZValue(1)
            text_item.setDefaultTextColor(QColor("black") if color.lightness() > 64 else QColor("white"))

            self._scene.addItem(text_item)

            pen = QPen(QColor(0, 0, 0))  # opaque black
            pen.setWidth(2)  # 2-pixel border
            rect.setPen(pen)
            self._scene.addItem(rect)
