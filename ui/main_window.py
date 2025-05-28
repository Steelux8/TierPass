from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QProgressBar
from ..core.strength_checker import evaluate_password

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Strength Auditor")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Enter your password:")
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.result = QLabel("")
        self.progress = QProgressBar()
        self.progress.setRange(0, 4)

        self.input.textChanged.connect(self.update_feedback)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.progress)
        layout.addWidget(self.result)

        self.setLayout(layout)

    def update_feedback(self, password: str):
        score, feedback = evaluate_password(password)
        self.progress.setValue(score)
        self.result.setText(feedback)