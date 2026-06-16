import re
from typing import Dict

# Pre-compiled regex engine patterns ensure optimal execution speed during parsing operations
LINK_REGEX = re.compile(r'<([^>]+)>;\s*rel="([^"]+)"')

def parse_link_header(header: str | None) -> Dict[str, str]:
    """
    Extracts relational directions ('next', 'prev', 'last') from GitHub HTTP pagination strings.
    Example Input: '<https://api.github.com/user/repos?page=2>; rel="next"'
    """
    if not header:
        return {}
    
    links = {}
    matches = LINK_REGEX.findall(header)
    for url, rel in matches:
        links[rel] = url
    return links