from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QProgressBar, QTextEdit, QCheckBox
from core.evaluate_password import evaluate_password
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Strength Auditor - TierPass")
        self.resize(500, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Enter your password:")
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Normal)

        self.progress = QProgressBar()
        self.progress.setRange(0, 4)

        self.result = QLabel("")

        self.show_details_checkbox = QCheckBox("Show detailed analysis")
        self.show_details_checkbox.stateChanged.connect(self.toggle_details_visibility)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Check the box above to show detailed analysis.")
        self.details.setText("")

        self.input.textChanged.connect(self.update_feedback)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.progress)
        layout.addWidget(self.result)
        layout.addWidget(self.show_details_checkbox)  # Checkbox above QTextEdit
        layout.addWidget(self.details)

        self.setLayout(layout)
        self.update_feedback("")

    def toggle_details_visibility(self, state):
        if state == 2:  # Checked
            self.details.setPlaceholderText("Detailed password analysis will appear here...")
            self.details.setText(self._last_details_text if hasattr(self, "_last_details_text") else "")
        else:
            self.details.setPlaceholderText("Check the box above to show detailed analysis.")
            self.details.clear()

    def update_feedback(self, password: str):
        score, feedback, analysis, guesses, calc_time, crack_times_display = evaluate_password(password)
        self.progress.setValue(score)

        # Build detailed feedback
        guesses_str = f"{guesses:,}" if guesses else "N/A"
        calc_time_str = f"{calc_time:.2f} seconds" if calc_time else "N/A"

        # Pick some common cracking scenarios to display
        offline_fast = crack_times_display.get('offline_fast_hashing_1e10_per_second', 'N/A')
        offline_slow = crack_times_display.get('offline_slow_hashing_1e4_per_second', 'N/A')
        online_throttled = crack_times_display.get('online_throttling_100_per_hour', 'N/A')

        feedback_text = (
            f"🔐 Estimated guesses needed: {guesses_str}\n"
            f"⏱️ Estimated calc time: {calc_time_str}\n\n"
            f"💻 Crack time (offline fast, 10B/sec): {offline_fast}\n"
            f"🐢 Crack time (offline slow, 10K/sec): {offline_slow}\n"
            f"🌐 Crack time (online throttled): {online_throttled}\n\n"
            f"{feedback}"
        )

        self.result.setText(feedback_text)

        details_text = self.format_sequence_matches(analysis)
        self._last_details_text = details_text

        if self.show_details_checkbox.isChecked():
            self.details.setText(details_text)
        else:
            self.details.clear()


    def format_sequence_matches(self, analysis: dict) -> str:
        sequences = analysis.get('sequence', [])
        if not sequences:
            return "No notable patterns found. Password appears strong."

        lines = []
        for match in sequences:
            pattern = match.get('pattern', 'unknown')
            token = match.get('token', '')
            i = match.get('i', '?')
            j = match.get('j', '?')

            line = f"Pattern: {pattern}, Text: '{token}', Position: [{i}-{j}]"

            if pattern == 'dictionary':
                line += f", Dictionary: {match.get('dictionary_name', '')}"
            elif pattern == 'sequence':
                line += f", Sequence: {match.get('sequence_name', '')}"
            elif pattern == 'repeat':
                line += f", Repeated {match.get('repeat_count', 1)} times"
            elif pattern == 'spatial':
                line += f", Keyboard graph: {match.get('graph', '')}"
            elif pattern == 'date':
                line += f", Date: {match.get('separator', '')}{match.get('year', '')}"

            lines.append(line)

        return "\n".join(lines)