"""Pure QR code generation logic — no Qt imports, fully unit-testable.

Uses the ``qrcode`` package's boolean matrix output only (``get_matrix``)
rather than its image-rendering path, which requires Pillow — the widget
rasterizes the matrix itself with Qt, so no imaging dependency beyond
``qrcode`` itself is needed.
"""

from __future__ import annotations

import qrcode
import qrcode.constants

from app.core.exceptions import ValidationError

ERROR_CORRECTION_LEVELS: dict[str, int] = {
    "Low (7%)": qrcode.constants.ERROR_CORRECT_L,
    "Medium (15%)": qrcode.constants.ERROR_CORRECT_M,
    "Quartile (25%)": qrcode.constants.ERROR_CORRECT_Q,
    "High (30%)": qrcode.constants.ERROR_CORRECT_H,
}

_MAX_DATA_LENGTH = 2953  # QR spec cap at version 40 / error-correct L


def generate_matrix(data: str, error_correction: str = "Medium (15%)") -> list[list[bool]]:
    if not data:
        raise ValidationError("Enter text or a URL to encode")
    if len(data) > _MAX_DATA_LENGTH:
        raise ValidationError(f"Data too long for a QR code (max {_MAX_DATA_LENGTH} characters)")
    if error_correction not in ERROR_CORRECTION_LEVELS:
        raise ValidationError(f"Unknown error correction level: {error_correction}")

    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECTION_LEVELS[error_correction],
        box_size=1,
        border=2,
    )
    qr.add_data(data)
    try:
        qr.make(fit=True)
    except (qrcode.exceptions.DataOverflowError, ValueError) as exc:
        # qrcode raises a bare ValueError (not DataOverflowError) when
        # best_fit() can't find a version 1-40 that holds the data at this
        # error-correction level — that ceiling is much lower for High
        # than for Low, so _MAX_DATA_LENGTH alone can't catch it upfront.
        raise ValidationError("Data too long for a QR code at this error correction level") from exc

    return qr.get_matrix()
