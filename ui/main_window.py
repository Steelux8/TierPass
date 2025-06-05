from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QProgressBar, QTextEdit, QCheckBox, QGroupBox
from core.evaluate_password import evaluate_password
class MainWindow(QWidget):
    TOOLTIPS = {
        "guesses": (
            "🔐 Estimated number of guesses needed to crack the password, based on detected patterns and randomness.\n"
            "This number is independent of how fast guesses can be made."
        ),

        "calc_time": (
            "⏱️ Estimated time to compute the password evaluation (not cracking time). Used to measure analysis speed, not attack speed."
        ),

        "online_throttled": (
            "🌐 Online throttled attack (100 guesses/hour):\n"
            "Simulates an attacker trying to guess a password through a live login form that rate-limits or locks accounts after a few failed attempts.\n\n"
            "**Requirements:** Only the victim’s username/email. No hash is needed.\n"
            "**How it works:** The attacker guesses passwords manually or with a script, but is slowed by protections like CAPTCHA or lockout.\n"
            "**Limitations:** Extremely slow; most accounts would lock long before 100 guesses.\n"
            "**Compared to others:** This is the most restricted attack scenario and takes the longest."
        ),

        "offline_slow": (
            "🐢 Offline slow hashing (10,000 guesses/second):\n"
            "Used when an attacker obtains a password hash (from a database breach) and the system uses secure, slow hashing like bcrypt or scrypt.\n\n"
            "✅ **Requires:** Leaked password hash (not plaintext), algorithm used, and any salts/costs.\n"
            "🧠 **How it works:** The attacker runs a brute-force or dictionary attack locally. No server involved — no login forms, no timeouts.\n"
            "💡 **Why it's slow:** Hashing functions like bcrypt are intentionally designed to take time per guess, slowing down attacks.\n"
            "🆚 **Compared to others:** Much faster than online guesses but slower than attacks on insecure hashes."
        ),

        "offline_fast": (
            "💻 Offline fast hashing (10 billion guesses/second):\n"
            "Assumes the attacker has stolen a password hash and it was hashed using a fast, outdated algorithm like MD5 or SHA-1.\n\n"
            "✅ **Requires:** A leaked password hash (not a password), often from insecure database storage.\n"
            "🧠 **How it works:** The attacker performs local cracking using powerful hardware (e.g., GPUs, botnets). No need to interact with the target system.\n"
            "🚫 **No login attempts:** This attack is entirely offline. The attacker doesn't risk lockouts or CAPTCHAs.\n"
            "⚠️ **Why it’s dangerous:** Without proper hashing, billions of guesses per second are possible.\n"
            "🆚 **Compared to others:** This is the fastest and most dangerous cracking scenario."

        ),
    }

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

        # Create individual labels
        self.labels = {
            "guesses": QLabel(),
            "calc_time": QLabel(),
            "online_throttled": QLabel(),
            "offline_slow": QLabel(),
            "offline_fast": QLabel()
        }

        # Add tooltips
        for key, label in self.labels.items():
            label.setToolTip(self.TOOLTIPS.get(key, ""))

        # Group all attack effort estimates together
        crack_effort_group = QGroupBox("Password Crack Time Estimates")
        crack_effort_layout = QVBoxLayout()
        for key in ["guesses", "calc_time", "online_throttled", "offline_slow", "offline_fast"]:
            crack_effort_layout.addWidget(self.labels[key])
        crack_effort_group.setLayout(crack_effort_layout)

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
        layout.addWidget(crack_effort_group)
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

        guesses_str = f"{guesses:,}" if guesses else "N/A"
        calc_time_str = f"{calc_time:.2f} seconds" if calc_time else "N/A"

        offline_fast = crack_times_display.get('offline_fast_hashing_1e10_per_second', 'N/A')
        offline_slow = crack_times_display.get('offline_slow_hashing_1e4_per_second', 'N/A')
        online_throttled = crack_times_display.get('online_throttling_100_per_hour', 'N/A')

        # Update each label individually
        self.labels["guesses"].setText(f"🔐 Estimated guesses needed: {guesses_str}")
        self.labels["calc_time"].setText(f"⏱️ Estimated calc time: {calc_time_str}")
        self.labels["online_throttled"].setText(f"🌐 Crack time (online throttled): {online_throttled}")
        self.labels["offline_slow"].setText(f"🐢 Crack time (offline slow, 10K/sec): {offline_slow}")
        self.labels["offline_fast"].setText(f"💻 Crack time (offline fast, 10B/sec): {offline_fast}")

        self.result.setText(feedback)

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