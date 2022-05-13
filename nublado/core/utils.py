import markdown2


def remove_lead_and_trail_slash(s):
    if s.startswith('/'):
        s = s[1:]
    if s.endswith('/'):
        s = s[:-1]
    return s


def strip_outer_html_tags(s):
    """ strips outer html tags """

    start = s.find('>') + 1
    end = len(s) - s[::-1].find('<') - 1
    return s[start:end]


def markdown_to_html(text, strip_outer_tags=False, extras=['fenced-code-blocks']):
    if not text:
        return ''
    html = markdown2.markdown(text, extras=extras)
    if strip_outer_tags:
        html = strip_outer_html_tags(html)
    return html
