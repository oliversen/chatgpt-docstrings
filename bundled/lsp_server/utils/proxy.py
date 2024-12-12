import re
from dataclasses import dataclass


@dataclass
class Proxy:
    """Represents a proxy configuration."""

    url: str
    authorization: str
    strict_ssl: bool


def is_valid_proxy(url: str) -> bool:
    """
    Checks if the given proxy URL matches a valid proxy format.

    A valid proxy URL follows the structure:
    <protocol>://[<username>:<password>@]<host>:<port>
    where:
    - protocol is either 'http', 'https', 'socks4' or 'socks5'
    - username and password are optional
    - host can be a domain or an IP address
    - port must be a valid number from 1 to 65535
    """
    PROXY_URL_PATTERN = (
        r"^((https?|socks[4,5]):\/\/)"  # Protocol
        r"(\w+:\w*@)?"  # Optional username and password
        r"(([a-zA-Z0-9-]+\.)+"  # Subdomain(s)
        r"[a-zA-Z]{2,}"  # Top-level domain
        r"|\d{1,3}(\.\d{1,3}){3})"  # IP address
        r"(:\d{1,5})$"  # Port
    )
    return bool(re.fullmatch(PROXY_URL_PATTERN, url))