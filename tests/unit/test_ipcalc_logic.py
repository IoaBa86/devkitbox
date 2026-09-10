from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.ipcalc.logic import calculate_subnet


def test_calculate_subnet_basic_slash24():
    info = calculate_subnet("192.168.1.0/24")
    assert info.ip_version == 4
    assert info.network_address == "192.168.1.0"
    assert info.broadcast_address == "192.168.1.255"
    assert info.netmask == "255.255.255.0"
    assert info.total_addresses == 256
    assert info.usable_hosts == 254
    assert info.first_usable == "192.168.1.1"
    assert info.last_usable == "192.168.1.254"
    assert info.is_private is True


def test_calculate_subnet_slash32_single_host():
    info = calculate_subnet("10.0.0.5/32")
    assert info.total_addresses == 1
    assert info.usable_hosts == 1
    assert info.first_usable == "10.0.0.5"
    assert info.last_usable == "10.0.0.5"


def test_calculate_subnet_slash31_point_to_point():
    info = calculate_subnet("10.0.0.0/31")
    assert info.total_addresses == 2
    assert info.usable_hosts == 2


def test_calculate_subnet_host_bits_set_non_strict():
    # 192.168.1.5/24 should normalize to the containing network, not error.
    info = calculate_subnet("192.168.1.5/24")
    assert info.network_address == "192.168.1.0"


def test_calculate_subnet_bare_ip_defaults_to_slash32():
    info = calculate_subnet("8.8.8.8")
    assert info.prefix_length == 32
    assert info.network_address == "8.8.8.8"


def test_calculate_subnet_public_address_not_private():
    info = calculate_subnet("8.8.8.8/32")
    assert info.is_private is False


def test_calculate_subnet_ipv6():
    info = calculate_subnet("2001:db8::/64")
    assert info.ip_version == 6
    assert info.broadcast_address is None
    assert info.network_address == "2001:db8::"


def test_calculate_subnet_empty_raises():
    with pytest.raises(ValidationError):
        calculate_subnet("")


def test_calculate_subnet_invalid_raises():
    with pytest.raises(ValidationError):
        calculate_subnet("not-an-ip")


def test_calculate_subnet_wildcard_mask_is_inverse_of_netmask():
    info = calculate_subnet("10.0.0.0/24")
    assert info.wildcard_mask == "0.0.0.255"
