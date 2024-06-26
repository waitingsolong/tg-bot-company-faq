import re

# Define ban words and patterns to remove
BAN_WORDS = [
    'cookie policy', 'privacy policy', 'terms and conditions', 'login', 
    'sign in', 'register', 'contact us', 'submit', 'playback', 'unmute',
    'watch history', 'TV recommendations', 'try again later', 'watch on',
    'error message', 'session has expired', 'try restarting your device',
    'you agree', 'include playlist', 'copy link', 'videos you watch',
    'signed out', 'error occurred'
]

# Define patterns to remove using specific characters and ranges
BAN_PATTERNS = [
    r'https?://[^\s]+',        # URLs
    r'[\U0001F600-\U0001F64F]', # Emoticons
    r'[\U0001F300-\U0001F5FF]', # Symbols & pictographs
    r'[\U0001F680-\U0001F6FF]', # Transport & map symbols
    r'[\U0001F1E0-\U0001F1FF]'  # Flags (iOS)
]

def clean_markdown_contents(markdown_contents):
    cleaned_contents = []

    for content in markdown_contents:
        cleaned_lines = []
        for line in content.split('\n'):
            # Apply all patterns to remove unnecessary information
            for pattern in BAN_PATTERNS:
                line = re.sub(pattern, '', line.strip())

            # Remove lines with ban words
            if any(ban_word in line.lower() for ban_word in BAN_WORDS):
                continue

            # Trim spaces
            cleaned_line = line.strip()

            # Remove short lines
            if len(cleaned_line) > 6:
                cleaned_lines.append(cleaned_line)

        # Join cleaned lines
        cleaned_content = '\n'.join(cleaned_lines)

        # Remove repetitive content by splitting and joining unique lines
        unique_lines = list(dict.fromkeys(cleaned_content.split('\n')))
        cleaned_contents.append('\n'.join(unique_lines))

    return cleaned_contents
