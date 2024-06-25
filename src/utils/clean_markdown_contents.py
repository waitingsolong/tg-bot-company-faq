import re


def clean_markdown_contents(markdown_contents: list[str]) -> list[str]:
    cleaned_contents = []

    for content in markdown_contents:
        cleaned_lines = []
        for line in content.split('\n'):
            # Remove URLs
            line = re.sub(r'\(https?://[^\)]+\)', '', line)
            # Remove markdown symbols and trim spaces
            cleaned_line = re.sub(r'[^\w\s]', '', line).strip()
            # Remove non-ASCII characters
            cleaned_line = re.sub(r'[^\x00-\x7F]+', '', cleaned_line)
            # Check for short strings and remove them
            if len(cleaned_line) > 6:
                cleaned_lines.append(cleaned_line)
        
        cleaned_contents.append('\n'.join(cleaned_lines))
    
    return cleaned_contents
