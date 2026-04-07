"""Playful computer vision-based gesture detection with sound effects and scoring."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional, Tuple
import math
import time
import random

import cv2
import numpy as np

Point = Tuple[int, int]


@dataclass
class GestureResult:
    gesture: str
    cursor: Optional[Point]
    landmarks: Optional[list]
    finger_states: Dict[str, bool]
    color: Tuple[int, int, int]
    score: int


class GestureDetector:
    """Playful gesture detection with sound effects, scoring, and color changing."""

    def __init__(
        self,
        max_num_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.5,
    ) -> None:
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)
        self.prev_cursor = None
        self.cursor_history: Deque[Point] = deque(maxlen=8)
        self.gesture_history = []
        self.frame_count = 0

        # Playful features
        self.colors = [
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 0, 255),    # Red
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Yellow
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (255, 20, 147), # Deep Pink
            (0, 191, 255),  # Deep Sky Blue
        ]
        self.current_color = 0
        self.last_color_change = time.time()
        self.score = 0
        self.last_gesture = 'idle'
        self.consecutive_gestures = 0
        self.multiplier = 1

        # Sound effect messages
        self.sound_effects = {
            'draw': ['🎨 Drawing!', '✏️  Sketching!', '🖌️  Painting!', '🎭 Creating art!'],
            'fist': ['✊ Fist power!', '💪 Strong fist!', '🥊 Punch detected!', '👊 Fist bump!'],
            'clear': ['🧹 Canvas cleared!', '🗑️  All gone!', '🔄 Fresh start!', '✨ Clean slate!'],
            'idle': ['⏸️  Paused', '😴 Resting', '🧘 Meditating', '🌙 Taking a break']
        }

    def get_feedback_sound(self, gesture: str) -> str:
        """Get a random sound effect message for the gesture."""
        effects = self.sound_effects.get(gesture, ['🤔 Detecting...'])
        return random.choice(effects)

    def get_random_color(self) -> Tuple[int, int, int]:
        """Return default color (palette selection now handles color changes)."""
        return self.colors[0]  # Green as default

    def update_score(self, gesture: str) -> None:
        """Update score based on gesture performance."""
        if gesture != 'idle':
            if gesture == self.last_gesture:
                self.consecutive_gestures += 1
                self.multiplier = min(self.consecutive_gestures // 3 + 1, 5)  # Max 5x multiplier
            else:
                self.consecutive_gestures = 1
                self.multiplier = 1

            points = 10 * self.multiplier
            self.score += points

            # Bonus for combos
            if self.consecutive_gestures >= 10:
                self.score += 50
                print(f"🎉 COMBO BONUS! +50 points! Total: {self.score}")

    def close(self) -> None:
        """Clean up resources."""
        pass

    def process(self, frame: np.ndarray) -> GestureResult:
        """Process frame and detect playful gestures."""
        self.frame_count += 1

        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)

        # Apply morphological operations to clean up the mask
        kernel = np.ones((7, 7), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.GaussianBlur(fg_mask, (7, 7), 0)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cursor = None
        gesture = "idle"

        if contours:
            # Find the largest contour (assumed to be the hand)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 3500:  # Minimum area threshold for hand detection
                # Get center of contour as cursor
                M = cv2.moments(largest_contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    cursor = (cx, cy)

                    perimeter = cv2.arcLength(largest_contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)

                        hull_area = 0
                        defect_count = 0
                        if len(largest_contour) >= 5:
                            hull_indices = cv2.convexHull(largest_contour, returnPoints=False)
                            if hull_indices is not None and len(hull_indices) > 3:
                                defects = cv2.convexityDefects(largest_contour, hull_indices)
                                if defects is not None:
                                    for i in range(defects.shape[0]):
                                        s, e, f, d = defects[i, 0]
                                        start = tuple(largest_contour[s][0])
                                        end = tuple(largest_contour[e][0])
                                        far = tuple(largest_contour[f][0])
                                        a = math.dist(start, end)
                                        b = math.dist(start, far)
                                        c = math.dist(end, far)
                                        if b * c > 0:
                                            angle = math.degrees(math.acos(max(min((b*b + c*c - a*a) / (2 * b * c), 1.0), -1.0)))
                                            # Lower defect depth threshold to detect fingers reliably on low-res masks
                                            if angle < 90 and d > 1000:
                                                defect_count += 1

                        hull = cv2.convexHull(largest_contour)
                        hull_area = cv2.contourArea(hull)
                        solidity = area / hull_area if hull_area > 0 else 1.0

                        # Try to estimate fingertip (preferred cursor when pointing)
                        fingertip = None
                        try:
                            pts = largest_contour.reshape(-1, 2)
                            centroid = np.array([cx, cy])
                            dists = np.linalg.norm(pts - centroid, axis=1)
                            idx = int(np.argmax(dists))
                            candidate = tuple(pts[idx])
                            # prefer candidates roughly above the centroid (smaller y)
                            if candidate[1] < centroid[1] + 60:
                                fingertip = candidate
                        except Exception:
                            fingertip = None

                        if circularity > 0.78:
                            gesture = "fist"  # More circular = fist
                        elif defect_count >= 4 and solidity < 0.85:
                            gesture = "clear"  # Open palm with several finger gaps
                        elif defect_count >= 1 or (solidity < 0.92 and len(hull) > 7):
                            gesture = "draw"  # Finger or pointing shape
                        else:
                            gesture = "idle"
                    else:
                        gesture = "idle"
                else:
                    gesture = "idle"
            else:
                gesture = "idle"
        else:
            gesture = "idle"

        # Prefer fingertip when pointing/drawing for more precise tracing
        if 'fingertip' in locals() and fingertip is not None and (gesture == 'draw' or gesture == 'idle'):
            cursor = fingertip

        if cursor is not None:
            self.cursor_history.append(cursor)
            if len(self.cursor_history) >= 3:
                avg = np.mean(np.array(self.cursor_history, dtype=np.float32), axis=0)
                cursor = (int(avg[0]), int(avg[1]))
        else:
            self.cursor_history.clear()

        # Update score and provide feedback
        if gesture != self.last_gesture and gesture != 'idle':
            self.update_score(gesture)
            sound = self.get_feedback_sound(gesture)
            color = self.get_random_color()
            if self.multiplier > 1:
                print(f"{sound} | {self.multiplier}x Combo! | Score: {self.score} | 🎨 {color}")
            else:
                print(f"{sound} | Score: {self.score} | 🎨 {color}")

        self.last_gesture = gesture

        # Smooth cursor position
        if cursor is not None and self.prev_cursor is not None:
            # Simple exponential smoothing
            alpha = 0.7
            cursor = (
                int(alpha * cursor[0] + (1 - alpha) * self.prev_cursor[0]),
                int(alpha * cursor[1] + (1 - alpha) * self.prev_cursor[1])
            )

        self.prev_cursor = cursor

        # Maintain gesture history for stability
        self.gesture_history.append(gesture)
        if len(self.gesture_history) > 5:
            self.gesture_history.pop(0)

        # Use majority vote for stable gestures
        if self.gesture_history:
            stable_gesture = max(set(self.gesture_history), key=self.gesture_history.count)
        else:
            stable_gesture = gesture

        finger_states = {"index": stable_gesture == "draw", "middle": False, "ring": False, "pinky": False}

        return GestureResult(
            gesture=stable_gesture,
            cursor=cursor,
            landmarks=None,
            finger_states=finger_states,
            color=self.get_random_color(),
            score=self.score
        )

    def draw_hand_annotations(
        self,
        frame: np.ndarray,
        landmarks: list,
    ) -> None:
        """Draw playful visual feedback."""
        # Draw a colorful circle at cursor position
        if hasattr(self, 'prev_cursor') and self.prev_cursor:
            color = self.get_random_color()
            cv2.circle(frame, self.prev_cursor, 15, color, 3)
            cv2.circle(frame, self.prev_cursor, 5, color, -1)
