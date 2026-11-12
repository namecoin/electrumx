import asyncio
from types import SimpleNamespace

import pytest
from aiorpcx import NetAddress

from electrumx.server.session import SessionManager


class MockSession:
    def __init__(self, remote_address):
        self._remote_address = remote_address

    def remote_address(self):
        return self._remote_address


def make_session_manager():
    manager = SessionManager.__new__(SessionManager)
    manager.env = SimpleNamespace(
        session_group_by_subnet_ipv4=24,
        session_group_by_subnet_ipv6=64,
    )
    manager.session_event = asyncio.Event()
    manager.sessions = {}
    manager.session_groups = {}
    return manager


@pytest.mark.parametrize('host, expected', (
    (None, 'unknown_addr'),
    ('8.8.8.8', '8.8.8.0/24'),
    ('192.168.1.2', None),
    ('2001:4860:4860::8888', '2001:4860:4860::/64'),
    ('fd00::1', None),
))
def test_ip_addr_group_name(host, expected):
    manager = make_session_manager()
    remote_address = NetAddress(host, 50001) if host is not None else None

    session = MockSession(remote_address)

    assert manager._ip_addr_group_name(session) == expected


def test_add_session_without_remote_address_uses_unknown_group():
    manager = make_session_manager()
    session = MockSession(None)

    manager.add_session(session)

    group = manager.session_groups['unknown_addr']
    assert manager.sessions[session] == (group,)
    assert group.sessions == {session}
