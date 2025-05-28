# zxcvbn Password Strength Analysis

TierPass uses the [zxcvbn](https://github.com/dropbox/zxcvbn) library (developed by Dropbox) to evaluate password strength using a data-driven and pattern-matching approach.

---

## What zxcvbn Checks

zxcvbn analyzes passwords using multiple pattern-detection strategies:

### 1. Dictionary Matches
- Common passwords (e.g., `123456`, `password`)
- English words
- First and last names
- Surnames
- Custom dictionaries (optional)

### 2. Keyboard Patterns
- Common keyboard walks (`asdf`, `qwerty`, `zxcvbn`)
- Reversed or shifted keyboard patterns

### 3. L33t Substitutions
- Detects character replacements like `@` → `a`, `0` → `o`, `!` → `i`
- These are often used in the gaming sphere and to fill special character demands

### 4. Repeats and Sequences
- Repeating characters or blocks (`aaa`, `abcabc`)
- Sequential numbers or letters (`123456`, `abcdef`)

### 5. Date Patterns
- Recognizes common date formats (e.g., `1999`, `05/12/2023`)
- Normalizes numeric-only dates like `052023`

---

## How Scoring Works

`zxcvbn` assigns a **score from 0 to 4** based on estimated cracking time:

| Score | Label         | Strength       | Crack Time (Offline, Slow Hashing)     |
|-------|---------------|----------------|----------------------------------------|
| 0     | Very Weak     | Instantly      | Instant                                |
| 1     | Weak          | Easy to guess  | Seconds or less                        |
| 2     | Fair          | Medium         | A few hours to a day                   |
| 3     | Strong        | Good           | Days to weeks                          |
| 4     | Very Strong   | Excellent      | Months to years                        |


---

## zxcvbn Output Structure

Calling `zxcvbn(password)` returns a dictionary with:

```json
{
  "password": "hunter2",
  "score": 1,
  "guesses": 1073,
  "feedback": {
    "warning": "This is a top-10 common password.",
    "suggestions": [
      "Add more words that are uncommon.",
      "Avoid keyboard patterns."
    ]
  },
  "crack_times_display": {
    "offline_slow_hashing_1e4_per_second": "less than a second",
    "offline_fast_hashing_1e10_per_second": "instant"
  },
  "sequence": [
    {
      "pattern": "dictionary",
      "dictionary_name": "passwords",
      "rank": 5,
      "token": "hunter"
    }
  ]
}