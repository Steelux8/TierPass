from typing import Any
from datetime import timedelta
from zxcvbn import zxcvbn

def evaluate_password(password: str) -> tuple[int, str, Any, Any, Any]:
    if not password:
        return 0, "Enter a password to evaluate.", {}, 0, {}

    result = zxcvbn(password)
    score = result['score']
    guesses = result.get('guesses', 0)

    crack_times_display = result.get('crack_times_display', {})

    suggestions = result['feedback']['suggestions']
    warning = result['feedback']['warning']

    feedback = ""
    if warning:
        feedback += f"⚠️ {warning}\n"
    if suggestions:
        feedback += "\n".join(suggestions)
    if not feedback:
        feedback = "✅ Strong password."
        
    return score, feedback, result, guesses, crack_times_display

