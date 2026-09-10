"""IP/Subnet Calculator tool page: CIDR math for IPv4 and IPv6."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.ipcalc.logic import calculate_subnet
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="ip_subnet_calculator",
    name="IP/Subnet Calculator",
    description="Calculate network/broadcast address, netmask, and usable host range for a CIDR block.",
    category="Network",
    keywords=("ip", "subnet", "cidr", "netmask", "network", "ipv4", "ipv6"),
)


class IpSubnetCalculatorTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Address / CIDR"))
        self._input = QLineEdit("192.168.1.0/24")
        self._input.textChanged.connect(self._refresh)
        input_row.addWidget(self._input, stretch=1)
        layout.addLayout(input_row)

        form = QFormLayout()
        self._labels: dict[str, QLabel] = {}
        for field in (
            "IP Version",
            "Network Address",
            "Broadcast Address",
            "Netmask",
            "Wildcard Mask",
            "Prefix Length",
            "Total Addresses",
            "Usable Hosts",
            "First Usable",
            "Last Usable",
            "Private Range",
        ):
            label = QLabel("—")
            form.addRow(field, label)
            self._labels[field] = label
        layout.addLayout(form)

        layout.addStretch(1)
        self._refresh()

    def build_actions(self, layout: QHBoxLayout) -> None:
        copy_button = QPushButton("Copy Network")
        copy_button.setObjectName("primaryButton")
        copy_button.clicked.connect(self._copy_network)
        layout.addWidget(copy_button)
        layout.addStretch(1)

    def _refresh(self) -> None:
        try:
            info = calculate_subnet(self._input.text())
        except ValidationError:
            for label in self._labels.values():
                label.setText("—")
            return

        self._labels["IP Version"].setText(f"IPv{info.ip_version}")
        self._labels["Network Address"].setText(info.network_address)
        self._labels["Broadcast Address"].setText(info.broadcast_address or "—")
        self._labels["Netmask"].setText(info.netmask)
        self._labels["Wildcard Mask"].setText(info.wildcard_mask)
        self._labels["Prefix Length"].setText(f"/{info.prefix_length}")
        self._labels["Total Addresses"].setText(f"{info.total_addresses:,}")
        self._labels["Usable Hosts"].setText(f"{info.usable_hosts:,}")
        self._labels["First Usable"].setText(info.first_usable or "—")
        self._labels["Last Usable"].setText(info.last_usable or "—")
        self._labels["Private Range"].setText("Yes" if info.is_private else "No")

    def _copy_network(self) -> None:
        text = self._labels["Network Address"].text()
        if not text or text == "—":
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
