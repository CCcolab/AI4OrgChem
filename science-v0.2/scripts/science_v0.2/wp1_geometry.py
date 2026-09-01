from __future__ import annotations

from typing import Any, Iterable


def d2h_geometry(parameters: Iterable[float]) -> list[list[Any]]:
    x, y, hx, hy = [float(item) for item in parameters]
    return [
        ["C", -x, -y, 0.0], ["C", -x, y, 0.0], ["C", x, y, 0.0], ["C", x, -y, 0.0],
        ["H", -hx, -hy, 0.0], ["H", -hx, hy, 0.0], ["H", hx, hy, 0.0], ["H", hx, -hy, 0.0],
    ]


def d4h_geometry(parameters: Iterable[float]) -> list[list[Any]]:
    c, h = [float(item) for item in parameters]
    return [
        ["C", -c, -c, 0.0], ["C", -c, c, 0.0], ["C", c, c, 0.0], ["C", c, -c, 0.0],
        ["H", -h, -h, 0.0], ["H", -h, h, 0.0], ["H", h, h, 0.0], ["H", h, -h, 0.0],
    ]
