import difflib


def generate_diff_html(original, modified):
    assert(type(original) == type(modified))
    if isinstance(original, list):
        original = '\n'.join(original)
    if isinstance(modified, list):
        modified = '\n'.join(modified)
        
    diff = difflib.ndiff(original.splitlines(), modified.splitlines())
    diff_html = []
    for line in diff:
        if line.startswith('+'):
            diff_html.append(f'<span style="color: green;">{line}</span>')
        elif line.startswith('-'):
            diff_html.append(f'<span style="color: red;">{line}</span>')
        else:
            diff_html.append(f'<span>{line}</span>')
    return '<br>'.join(diff_html)