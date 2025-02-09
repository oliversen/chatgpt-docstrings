import re
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Proxy:
    """Represents a proxy configuration."""

    url: str
    authorization: str = ""
    strict_ssl: bool = False

    def is_valid(
        self, allowed_protocols: Iterable[str] = ("http", "https", "socks4", "socks5")
    ) -> bool:
        """Checks if the proxy URL matches a valid proxy format.

        A valid proxy URL follows the structure:
        <protocol>://[<username>:<password>@]<host>:<port>
        where:
        - protocol is either 'http', 'https', 'socks4' or 'socks5' (by default)
        - username and password are optional
        - host can be a domain or an IP address
        - port must be a valid number from 1 to 65535
        """
        PROXY_URL_PATTERN = (
            rf"^(({'|'.join(allowed_protocols)}):\/\/)"  # Protocol
            r"(\w+:\w*@)?"  # Optional username and password
            r"(([a-zA-Z0-9-]+\.)+"  # Subdomain(s)
            r"[a-zA-Z]{2,}"  # Top-level domain
            r"|\d{1,3}(\.\d{1,3}){3})"  # IP address
            r"(:\d{1,5})$"  # Port
        )
        return bool(re.fullmatch(PROXY_URL_PATTERN, self.url))
