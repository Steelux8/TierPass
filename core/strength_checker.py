from zxcvbn import zxcvbn

def evaluate_password(password: str) -> tuple[int, str]:
    if not password:
        return 0, "Enter a password to evaluate."

    result = zxcvbn(password)
    score = result['score']  # 0 (weakest) to 4 (strongest)

    # Feedback generation
    suggestions = result['feedback']['suggestions']
    warning = result['feedback']['warning']

    feedback = ""
    if warning:
        feedback += f"⚠️ {warning}\n"
    if suggestions:
        feedback += "\n".join(suggestions)
    if not feedback:
        feedback = "✅ Strong password."

    return score, feedback