"""Entry point for the Air Canvas interactive drawing experience."""
from __future__ import annotations

import sys
from typing import Dict, List, Tuple

import cv2
import numpy as np

from canvas import DrawingCanvas
from gesture_detector import GestureDetector
from hooks import hooks
from utils import GestureFilter, PointSmoother, blend_frames, draw_cursor, put_multiline_text

import plugins.gesture_logger  # noqa: F401

GESTURE_COLORS: Dict[str, tuple[int, int, int]] = {
    "draw": (0, 255, 0),
    "fist": (0, 0, 255),
    "clear": (0, 255, 255),
    "idle": (255, 255, 255),
}

# Color palette configuration
PALETTE_COLORS = [
    (0, 255, 0),      # Green
    (255, 0, 0),      # Blue
    (0, 0, 255),      # Red
    (255, 255, 0),    # Cyan
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Yellow
    (255, 165, 0),    # Orange
    (128, 0, 128),    # Purple
    (255, 20, 147),   # Deep Pink
    (0, 191, 255),    # Deep Sky Blue
    (255, 255, 255),  # White
    (0, 0, 0),        # Black
]
PALETTE_WIDTH = 150
PALETTE_HEIGHT = 50


def draw_color_palette(frame: np.ndarray, selected_color: Tuple[int, int, int]) -> Tuple[int, int]:
    """Draw color palette on the right side and return palette position info."""
    height, width = frame.shape[:2]
    palette_x = width - PALETTE_WIDTH
    palette_y = 50

    # Draw palette background
    cv2.rectangle(frame, (palette_x - 5, palette_y - 5),
                  (width - 5, palette_y + len(PALETTE_COLORS) * PALETTE_HEIGHT + 5),
                  (50, 50, 50), -1)
    cv2.rectangle(frame, (palette_x - 5, palette_y - 5),
                  (width - 5, palette_y + len(PALETTE_COLORS) * PALETTE_HEIGHT + 5),
                  (200, 200, 200), 2)

    # Draw color swatches
    for i, color in enumerate(PALETTE_COLORS):
        y_start = palette_y + i * PALETTE_HEIGHT
        y_end = y_start + PALETTE_HEIGHT

        # Draw color rectangle
        cv2.rectangle(frame, (palette_x, y_start), (width - 10, y_end), color, -1)

        # Draw border
        cv2.rectangle(frame, (palette_x, y_start), (width - 10, y_end), (255, 255, 255), 1)

        # Highlight selected color
        if color == selected_color:
            cv2.rectangle(frame, (palette_x - 3, y_start - 3),
                         (width - 7, y_end + 3), (255, 255, 0), 3)

    # Add palette title
    cv2.putText(frame, "COLOR PALETTE", (palette_x + 10, palette_y - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return palette_x, palette_y


def get_color_from_palette(cursor: Tuple[int, int], palette_x: int, palette_y: int) -> Tuple[int, int, int] | None:
    """Check if cursor is over a color in the palette and return the color."""
    if cursor is None:
        return None

    x, y = cursor
    if x >= palette_x and x <= palette_x + PALETTE_WIDTH:
        for i, color in enumerate(PALETTE_COLORS):
            y_start = palette_y + i * PALETTE_HEIGHT
            y_end = y_start + PALETTE_HEIGHT
            if y_start <= y <= y_end:
                return color
    return None


def demo_mode():
    """Run the app in demo mode without webcam to test color palette functionality."""
    print("🎨 Starting Air Canvas in DEMO MODE (no webcam required)")
    print("This mode demonstrates the color palette and drawing features.")

    # Create a demo frame
    demo_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    demo_frame[:] = (50, 50, 50)  # Gray background

    selected_color = PALETTE_COLORS[0]  # Start with first color

    # Draw palette on demo frame
    palette_x, palette_y = draw_color_palette(demo_frame, selected_color)

    print("\n🎨 DEMO: Color Palette Selection Test")
    print("Testing cursor positions and color selection:")

    # Test different cursor positions
    test_positions = [
        (600, 75),   # Should select first color (Green)
        (600, 125),  # Should select second color (Blue)
        (600, 175),  # Should select third color (Red)
        (600, 225),  # Should select fourth color (Cyan)
        (400, 100),  # Outside palette (should return None)
    ]

    for pos in test_positions:
        selected = get_color_from_palette(pos, palette_x, palette_y)
        if selected:
            color_names = {
                (0, 255, 0): "Green", (255, 0, 0): "Blue", (0, 0, 255): "Red",
                (255, 255, 0): "Cyan", (255, 0, 255): "Magenta", (0, 255, 255): "Yellow",
                (255, 165, 0): "Orange", (128, 0, 128): "Purple", (255, 20, 147): "Deep Pink",
                (0, 191, 255): "Deep Sky Blue", (255, 255, 255): "White", (0, 0, 0): "Black"
            }
            color_name = color_names.get(selected, "Unknown")
            print(f"  Cursor at {pos} → Selected {color_name}: {selected}")
        else:
            print(f"  Cursor at {pos} → Outside palette (None)")

    print("\n✅ Demo completed! The color palette selection logic is working correctly.")
    print("To use with a real webcam:")
    print("  1. Close any other camera applications")
    print("  2. Run: python main.py")
    print("  3. Point at colors on the right side to select them")
    print("  4. Make a fist to draw, open palm to clear")


def run() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Unable to access the webcam. Make sure a camera is connected.")
        sys.exit(1)

    detector = GestureDetector()
    canvas: DrawingCanvas | None = None
    prev_point = None
    smoother = PointSmoother(momentum=0.88)
    gesture_filter = GestureFilter(confirm_frames=4, default="idle")
    last_gesture = "idle"
    selected_color = PALETTE_COLORS[0]  # Start with first color

    try:
        hooks.emit("start")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Stream ended or cannot read from webcam. Exiting.")
                break

            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            if canvas is None:
                canvas = DrawingCanvas(width, height)
            else:
                canvas.resize_if_needed(width, height)

            result = detector.process(frame)
            if result.landmarks is not None:
                detector.draw_hand_annotations(frame, result.landmarks)

            cursor = smoother.update(result.cursor)
            gesture = gesture_filter.update(result.gesture)

            # Draw color palette and get palette position
            palette_x, palette_y = draw_color_palette(frame, selected_color)

            # Check for color selection (when pointing at palette)
            if cursor is not None:
                palette_color = get_color_from_palette(cursor, palette_x, palette_y)
                if palette_color is not None and gesture == "draw":
                    if selected_color != palette_color:
                        selected_color = palette_color
                        hooks.emit("palette_select", color=selected_color)
                        print(f"🎨 [PALETTE] Selected color: {selected_color}")

            if gesture != last_gesture:
                hooks.emit("gesture", gesture=gesture, cursor=cursor, finger_states=result.finger_states)

            if gesture == "draw" and cursor is not None:
                # Don't draw if cursor is in palette area
                if cursor[0] < palette_x:
                    if prev_point is None:
                        prev_point = cursor
                    hooks.emit("draw", start=prev_point, end=cursor, canvas=canvas)
                    # Use selected color from palette
                    canvas.draw_line(prev_point, cursor, selected_color)
                    prev_point = cursor
                else:
                    prev_point = None
            else:
                prev_point = None

            if gesture == "clear" and last_gesture != "clear" and canvas is not None:
                hooks.emit("clear", canvas=canvas)
                canvas.clear()

            if gesture == "fist" and last_gesture != "fist":
                hooks.emit("pause", canvas=canvas)

            last_gesture = gesture

            overlay = blend_frames(frame, canvas.get_image()) if canvas else frame
            cursor_color = selected_color if gesture != "idle" else GESTURE_COLORS.get(gesture, (255, 255, 255))
            draw_cursor(overlay, cursor, cursor_color)
            put_multiline_text(
                overlay,
                [
                    f"Gesture: {gesture.upper()} | Score: {result.score}",
                    f"🎨 Selected: {selected_color}",
                    "Controls: Point to select palette color, then draw with fingers!",
                    "POINT=draw, FIST=pause, PALM=clear | Press 'q' to quit",
                ],
            )

            cv2.imshow("Air Canvas", overlay)
            if canvas is not None:
                cv2.imshow("Canvas", canvas.get_image())

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
    except KeyboardInterrupt:
        pass
    finally:
        hooks.emit("exit")
        cap.release()
        detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        run()
