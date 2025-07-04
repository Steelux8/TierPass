from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QProgressBar, QTextEdit, QCheckBox, QGroupBox, QPushButton
)
from PyQt6.QtCore import Qt
from core.evaluate_password import evaluate_password
from core.password_generator import generate_strong_password
from ui.entropy_chart import EntropyChart


class MainWindow(QWidget):
    TOOLTIPS = {
        "guesses": (
            "🔐 Estimated number of guesses needed to crack the password, based on detected patterns and randomness.\n"
            "This number is independent of how fast guesses can be made."
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
        self.resize(1000, 500)

        # Outer layout
        outer_layout = QHBoxLayout()

        # Create layouts for each password section
        self.sections = []
        for i in range(2):
            section = self.build_password_section(i)
            outer_layout.addLayout(section["layout"])
            self.sections.append(section)

        self.setLayout(outer_layout)

        # Initial update for both
        self.update_feedback(0, "")
        self.update_feedback(1, "")

    def build_password_section(self, index: int):
        layout = QVBoxLayout()

        label = QLabel(f"Enter password #{index + 1}:")
        input_field = QLineEdit()
        input_field.setEchoMode(QLineEdit.EchoMode.Normal)
        input_field.setMaxLength(72)
        input_field.textChanged.connect(lambda text, i=index: self.update_feedback(i, text))

        progress = QProgressBar()
        progress.setRange(0, 4)
        
        generate_btn = None
        if index == 0:
            generate_btn = QPushButton("Generate Word Password")
            generate_btn.clicked.connect(lambda _, i=index: self.fill_generated_password(i))
        if index == 1:
            generate_btn = QPushButton("Generate Symbol Password")
            generate_btn.clicked.connect(lambda _, i=index: self.fill_generated_password(i))

        result = QLabel()

        # Create individual labels
        labels = {
            "guesses": QLabel(),
            "calc_time": QLabel(),
            "online_throttled": QLabel(),
            "offline_slow": QLabel(),
            "offline_fast": QLabel()
        }

        # Add tooltips
        for key, label_widget in labels.items():
            label_widget.setToolTip(self.TOOLTIPS.get(key, ""))

        crack_effort_group = QGroupBox("Crack Time Estimates")
        crack_effort_layout = QVBoxLayout()
        for key in ["guesses", "calc_time", "online_throttled", "offline_slow", "offline_fast"]:
            crack_effort_layout.addWidget(labels[key])
        crack_effort_group.setLayout(crack_effort_layout)

        show_details_checkbox = QCheckBox("Show detailed analysis")
        
        # Container widget for details text and entropy chart stacked vertically
        details_container = QWidget()
        details_layout = QVBoxLayout()
        details_container.setLayout(details_layout)

        details = QTextEdit()
        details.setReadOnly(True)
        details.setPlaceholderText("Check the box above to show detailed analysis.")
        details.setText("")
        details_layout.addWidget(details)

        entropy_chart = EntropyChart()
        entropy_chart.hide()  # Initially hidden
        details_layout.addWidget(entropy_chart)

        # Manage visibility
        def toggle_details(state, i=index):
            section = self.sections[i]
            if state == 2:
                section["details"].setPlaceholderText("Detailed password analysis will appear here...")
                section["details"].setText(section.get("_last_details_text", ""))
                section["entropy_chart"].show()
            else:
                section["details"].setPlaceholderText("Check the box above to show detailed analysis.")
                section["details"].clear()
                section["entropy_chart"].hide()

        show_details_checkbox.stateChanged.connect(toggle_details)

        # Add widgets to layout
        layout.addWidget(label)
        layout.addWidget(input_field)
        layout.addWidget(progress)

        # Feedback + optional generate button in same horizontal layout
        feedback_row = QHBoxLayout()
        feedback_row.addWidget(result)

        if generate_btn:  # only for section #2
            feedback_row.addStretch()  # push the button to the right
            feedback_row.addWidget(generate_btn)

        layout.addLayout(feedback_row)
        layout.addWidget(result)
        layout.addWidget(crack_effort_group)
        layout.addWidget(show_details_checkbox)
        layout.addWidget(details_container)

        entropy_chart = EntropyChart()
        layout.addWidget(entropy_chart)

        return {
            "layout": layout,
            "input": input_field,
            "progress": progress,
            "result": result,
            "labels": labels,
            "details": details,
            "checkbox": show_details_checkbox,
            "entropy_chart": entropy_chart,
        }

    def fill_generated_password(self, index: int):
        """
        Generate a strong password and drop it
        into the second (index 1) input field.
        """
        if index == 0:
            pwd = generate_strong_password(style="words")
            self.sections[0]["input"].setText(pwd)
        elif index == 1:
            pwd = generate_strong_password(style="symbols")
            self.sections[1]["input"].setText(pwd)
    
    def contextual_feedback(self, sequence: list[dict]) -> list[str]:
        feedback = []

        for match in sequence:
            token = match.get('token', '')
            pattern = match.get('pattern', 'unknown')

            if pattern == 'repeat':
                feedback.append(f"⚠️ Repeated sequence found: '{token}'")
            elif pattern == 'sequence':
                name = match.get('sequence_name', 'sequence')
                feedback.append(f"⚠️ Predictable sequence: '{token}' ({name})")
            elif pattern == 'spatial':
                graph = match.get('graph', '')
                feedback.append(f"⚠️ Keyboard pattern: '{token}' ({graph})")
            elif pattern == 'dictionary':
                dict_name = match.get('dictionary_name', '')
                feedback.append(f"⚠️ Common word found: '{token}' ({dict_name})")
            elif pattern == 'date':
                year = match.get('year')
                feedback.append(f"⚠️ Date detected in password: '{token}' (Year: {year})")
            elif pattern == 'regex':
                feedback.append(f"⚠️ Regex pattern match: '{token}'")
            elif pattern == 'bruteforce':
                feedback.append(f"⚠️ Weak segment: '{token}' appears random but short")

        return feedback
    
    def update_feedback(self, index: int, password: str):
        section = self.sections[index]
        score, base_feedback, analysis, guesses, crack_times_display = evaluate_password(password)
        sequence = analysis.get('sequence', [])

        # Get contextual observations
        context_lines = self.contextual_feedback(sequence)

        # Combine base feedback with contextual notes
        feedback = base_feedback.strip()
        if context_lines:
            feedback += "\n\n" + "\n".join(context_lines)

        section["progress"].setValue(score)

        guesses_str = f"{guesses:,}" if guesses else "N/A"

        offline_fast = crack_times_display.get('offline_fast_hashing_1e10_per_second', 'N/A')
        offline_slow = crack_times_display.get('offline_slow_hashing_1e4_per_second', 'N/A')
        online_throttled = crack_times_display.get('online_throttling_100_per_hour', 'N/A')

        # Update labels
        section["labels"]["guesses"].setText(f"🔐 Estimated guesses needed: {guesses_str}")
        section["labels"]["online_throttled"].setText(f"🌐 Crack time (online throttled): {online_throttled}")
        section["labels"]["offline_slow"].setText(f"🐢 Crack time (offline slow): {offline_slow}")
        section["labels"]["offline_fast"].setText(f"💻 Crack time (offline fast): {offline_fast}")

        section["result"].setText(feedback)

        details_text = self.format_sequence_matches(analysis)
        section["_last_details_text"] = details_text

        if section["checkbox"].isChecked():
            section["details"].setText(details_text)
            section["entropy_chart"].show()
        else:
            section["details"].clear()
            section["entropy_chart"].hide()

        section["entropy_chart"].update_chart(password, analysis.get("sequence", []))

    def format_sequence_matches(self, analysis: dict) -> str:
        password = analysis.get('password', '')
        if not password:
            return "No password entered. Please type or generate one to see feedback."

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
