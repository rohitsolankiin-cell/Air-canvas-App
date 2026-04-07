"""Canvas abstraction to accumulate brush strokes."""
from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np

Point = Tuple[int, int]
Color = Tuple[int, int, int]


class DrawingCanvas:
    """Stores a persistent drawing surface that matches the camera feed."""

    def __init__(
        self,
        width: int,
        height: int,
        line_color: Color = (0, 191, 255),
        thickness: int = 6,
    ) -> None:
        self.line_color = line_color
        self.thickness = thickness
        self._init_surface(width, height)

    def _init_surface(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.surface = np.zeros((height, width, 3), dtype=np.uint8)

    def resize_if_needed(self, width: int, height: int) -> None:
        """Ensure the canvas matches the latest frame shape."""
        if width != self.width or height != self.height:
            self._init_surface(width, height)

    def draw_line(self, start: Point | None, end: Point | None, color: Color | None = None) -> None:
        """Draw an anti-aliased stroke between two finger positions."""
        if start is None or end is None:
            return
        draw_color = color if color is not None else self.line_color
        cv2.line(self.surface, start, end, draw_color, self.thickness, cv2.LINE_AA)

    def clear(self) -> None:
        """Clear the canvas while preserving settings."""
        self.surface.fill(0)

    def get_image(self) -> np.ndarray:
        """Expose the raw canvas image for rendering."""
        return self.surface
