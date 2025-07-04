# password_generator.py
import secrets
import string
from zxcvbn import zxcvbn
import os

_ALPHABET = (
    string.ascii_lowercase +
    string.ascii_uppercase +
    string.digits +
    "!@#$%^&*()-_=+[]{}"
)

def _random_password_words(length: int = 20) -> str:
    # Load wordlist
    wordlist_path = "/usr/share/dict/words"
    if os.path.exists(wordlist_path):
        with open(wordlist_path) as f:
            words = [w.strip().lower() for w in f if 3 <= len(w.strip()) <= 8 and w.isalpha()]
    else:
        words = ["apple", "green", "flame", "lucky", "monkey", "river", "stone", "guitar", "storm", "rabbit"]

    words = list(set(words))  # remove duplicates in wordlist itself just in case
    secrets.SystemRandom().shuffle(words)  # shuffle to randomize selection

    chosen = []
    total_length = 0

    for word in words:
        capitalized = word.capitalize()
        if total_length + len(capitalized) > length:
            break
        chosen.append(capitalized)
        total_length += len(capitalized)

    return ''.join(chosen)

def _random_password_symbols(length: int = 16) -> str:
    """Return a single random password of `length` characters."""
    return ''.join(secrets.choice(_ALPHABET) for _ in range(length))

def generate_strong_password(style: str = "words", min_score: int = 4, max_tries: int = 100) -> str:
    """
    Keep generating random passwords until zxcvbn gives `min_score`
    (default 4 = ‘very strong’).  Hard-limit attempts to `max_tries`
    to avoid an infinite loop in pathological environments.
    """
    if style == "words":
        for _ in range(max_tries):
            pwd = _random_password_words()
            if zxcvbn(pwd)["score"] >= min_score:
                return pwd
    elif style == "symbols":
        for _ in range(max_tries):
            pwd = _random_password_symbols()
            if zxcvbn(pwd)["score"] >= min_score:
                return pwd
    raise RuntimeError(
        f"Couldn’t generate a password scoring ≥ {min_score} in {max_tries} tries"
    )
