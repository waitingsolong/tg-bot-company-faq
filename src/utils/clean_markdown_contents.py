import re

# Define ban words and patterns to remove
BAN_WORDS = [
    'cookie policy', 'privacy policy', 'terms and conditions', 'login', 
    'sign in', 'register', 'contact us', 'submit', 'playback',
    'watch history', 'TV recommendations', 'try again later', 'watch on',
    'error message', 'session has expired', 'try restarting your device',
    'you agree', 'include playlist', 'copy link', 'videos you watch',
    'signed out', 'error occurred', 'share this video', 'show transcript',
    'words on screen', 'appears on screen', 'read more', 'click here',
    'learn more', 'advertisement', 'sponsored', 'terms of use', 'about us',
    'careers', 'press releases', 'site map', 'faq', 'help center', 
    'customer support', 'feedback', 'user agreement', 'disclaimer', 
    'copyright', 'all rights reserved', 'privacy notice', 'accessibility',  
    'related articles', 'related videos', 'more info', 'next video', 
    'previous video', 'click to expand', 'click to collapse', 'join now', 
    'free trial', 'sign up', 'log out', 'view details', 'contact support',
    'report issue', 'legal notice', 'powered by', 'follow us', 'connect with us',
    'featured', 'top stories', 'breaking news', 'live updates', 'trending',
    'back to top', 'site navigation', 'cookie consent',
    'close ad', 'skip ad', 'next page', 'page not found',
    'error 404', 'home page', 'webmaster', 'terms of service', 'last updated',
    'print this page', 'save as pdf', 'related content', 'join the conversation',
    'sign in to comment', 'add a comment', 'view replies', 'hide replies',
    'video unavailable', 'no longer available', 'start free trial', 'limited time offer',
    'read full article', 'learn more here', 'download now', 'get started', 
    'click to learn more', 'watch full video', 'continue watching', 'recommended for you',
    'watch next', 'play next', 'now playing', 'up next', 'thanks for watching'
]

# Define patterns to remove using specific characters and ranges
BAN_PATTERNS = [
    r'https?://[^\s]+',        # URLs
    r'[\U0001F600-\U0001F64F]', # Emoticons
    r'[\U0001F300-\U0001F5FF]', # Symbols & pictographs
    r'[\U0001F680-\U0001F6FF]', # Transport & map symbols
    r'[\U0001F1E0-\U0001F1FF]',  # Flags (iOS)
    r'^\s*[\-\*]+\s*$',        # Lines with only dashes or asterisks
    r'^\s*[\-\*]\s+.*$',       # List items
    r'\[.*?\]\(.*?\)',         # Markdown links
    r'^\[.*?\]\(.*?\)$',       # Video links
    r'^\d{1,2}:\d{2}\s+to\s+watch$' # Watch time lines
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
