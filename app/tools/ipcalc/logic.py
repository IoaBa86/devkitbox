"""Pure IP/subnet calculation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from app.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class SubnetInfo:
    ip_version: int
    network_address: str
    broadcast_address: str | None
    netmask: str
    wildcard_mask: str
    prefix_length: int
    total_addresses: int
    usable_hosts: int
    first_usable: str | None
    last_usable: str | None
    is_private: bool


def calculate_subnet(cidr_text: str) -> SubnetInfo:
    text = cidr_text.strip()
    if not text:
        raise ValidationError("Enter an address, e.g. 192.168.1.0/24")
    if "/" not in text:
        text = f"{text}/32"

    try:
        network = ipaddress.ip_network(text, strict=False)
    except ValueError as exc:
        raise ValidationError(f"Invalid address or CIDR: {cidr_text!r}", detail=str(exc)) from exc

    total = network.num_addresses
    if network.version == 4 and network.prefixlen <= 30:
        usable_hosts = total - 2
        first_usable = str(network.network_address + 1)
        last_usable = str(network.broadcast_address - 1)
    elif total >= 2:
        usable_hosts = total
        first_usable = str(network.network_address)
        last_usable = str(network[-1])
    else:
        usable_hosts = total
        first_usable = str(network.network_address)
        last_usable = str(network.network_address)

    return SubnetInfo(
        ip_version=network.version,
        network_address=str(network.network_address),
        broadcast_address=str(network.broadcast_address) if network.version == 4 else None,
        netmask=str(network.netmask),
        wildcard_mask=str(network.hostmask),
        prefix_length=network.prefixlen,
        total_addresses=total,
        usable_hosts=usable_hosts,
        first_usable=first_usable,
        last_usable=last_usable,
        is_private=network.is_private,
    )
