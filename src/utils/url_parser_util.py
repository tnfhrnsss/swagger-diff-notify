from urllib.parse import urlparse

def extract_domain_port(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed_url = urlparse(url)

    domain = parsed_url.hostname
    port = parsed_url.port if parsed_url.port else (443 if parsed_url.scheme == 'https' else 80)

    return f"{domain}_{port}"
