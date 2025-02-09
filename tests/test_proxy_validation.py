from __future__ import annotations

from pytest import mark

from language_server.utils.proxy import Proxy


@mark.parametrize(
    "schema",
    [
        ("", False),
        ("socks://", False),
        ("socks4://", True),
        ("socks5://", True),
        ("http://", True),
        ("https://", True),
    ],
)
@mark.parametrize(
    "auth",
    [
        ("user:pass", False),
        ("user:", False),
        (":pass", False),
        (":pass@", False),
        ("", True),
        ("user:@", True),
        ("user:pass@", True),
    ],
)
@mark.parametrize(
    "host",
    [
        ("", False),
        ("proxy", False),
        ("127.0.0", False),
        ("proxy.com", True),
        ("sub.proxy.com", True),
        ("127.0.0.1", True),
    ],
)
@mark.parametrize(
    "port",
    [
        ("", False),
        (":", False),
        (":1", True),
        (":65535", True),
    ],
)
def test_proxy_url_validation(
    schema: tuple[str, bool],
    auth: tuple[str, bool],
    host: tuple[str, bool],
    port: tuple[str, bool],
) -> None:
    url = f"{schema[0]}{auth[0]}{host[0]}{port[0]}"
    valid = all((schema[1], auth[1], host[1], port[1]))
    if valid:
        assert Proxy(url).is_valid()
    else:
        assert not Proxy(url).is_valid()
