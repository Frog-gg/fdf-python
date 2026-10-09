from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """Точка карты с координатами и опциональным цветом."""

    x: int
    y: int
    z: int
    color: str | None = None


class Map:
    """Карта высот — сетка точек."""

    def __init__(self, points: list[list[Point]]) -> None:
        if not points or not points[0]:
            raise ValueError("Карта не может быть пустой")
        self._points = points
        self.height: int = len(points)
        self.width: int = len(points[0])

    def __len__(self) -> int:
        """Общее количество точек."""
        return self.width * self.height

    def __iter__(self) -> Iterator[Point]:
        """Обход всех точек построчно."""
        for row in self._points:
            yield from row

    def get(self, x: int, y: int) -> Point:
        """Получить точку по координатам."""
        return self._points[y][x]

    def neighbors(self, x: int, y: int) -> list[Point]:
        """Соседи справа и снизу (чтобы не рисовать ребра дважды)."""
        result: list[Point] = []
        if x + 1 < self.width:
            result.append(self._points[y][x + 1])
        if y + 1 < self.height:
            result.append(self._points[y + 1][x])
        return result