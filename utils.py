"""Utility helpers for the Air Canvas project."""
from typing import Sequence, Tuple

import cv2
import numpy as np

Color = Tuple[int, int, int]
Point = Tuple[int, int]


def blend_frames(frame: np.ndarray, canvas: np.ndarray, alpha: float = 0.4) -> np.ndarray:
    """Overlay the drawing canvas on top of the live frame."""
    alpha = min(max(alpha, 0.0), 1.0)
    beta = 1.0 - alpha
    return cv2.addWeighted(frame, beta, canvas, alpha, 0)


def draw_cursor(frame: np.ndarray, position: Point | None, color: Color, radius: int = 12) -> None:
    """Render a visual cursor to show where drawing will occur."""
    if position is None:
        return
    cv2.circle(frame, position, radius, color, 2, cv2.LINE_AA)
    cv2.circle(frame, position, max(2, radius // 2), color, -1, cv2.LINE_AA)


def put_multiline_text(
    frame: np.ndarray,
    lines: Sequence[str],
    origin: Point = (12, 28),
    color: Color = (255, 255, 255),
    line_height: int = 26,
) -> None:
    """Render stacked status text lines."""
    x, y = origin
    for line in lines:
        cv2.putText(
            frame,
            line,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )
        y += line_height


def ensure_canvas_size(canvas: np.ndarray, width: int, height: int) -> np.ndarray:
    """Return a canvas with the requested shape, reinitializing when needed."""
    if canvas.shape[1] == width and canvas.shape[0] == height:
        return canvas
    return np.zeros((height, width, 3), dtype=np.uint8)


class PointSmoother:
    """Simple exponential moving average to reduce cursor jitter."""

    def __init__(self, momentum: float = 0.7) -> None:
        self.momentum = min(max(momentum, 0.0), 0.99)
        self._state: np.ndarray | None = None

    def update(self, point: Point | None) -> Point | None:
        if point is None:
            self._state = None
            return None

        vector = np.array(point, dtype=np.float32)
        if self._state is None:
            self._state = vector
        else:
            self._state = self.momentum * self._state + (1.0 - self.momentum) * vector

        return int(self._state[0]), int(self._state[1])


class GestureFilter:
    """Temporal filter so gestures change only after repeated frames."""

    def __init__(self, confirm_frames: int = 3, default: str = "idle") -> None:
        self.confirm_frames = max(1, confirm_frames)
        self._current = default
        self._candidate: str | None = None
        self._count = 0

    def update(self, gesture: str) -> str:
        if gesture == self._current:
            self._candidate = None
            self._count = 0
            return self._current

        if self._candidate != gesture:
            self._candidate = gesture
            self._count = 1
        else:
            self._count += 1
            if self._count >= self.confirm_frames:
                self._current = gesture
                self._candidate = None
                self._count = 0

        return self._current
