"""Playful hook plugin for logging gesture lifecycle events with fun feedback."""

from __future__ import annotations
import random

from hooks import hooks


def _log_gesture(gesture: str, cursor: tuple[int, int] | None, finger_states: dict[str, bool], **kwargs) -> None:
    emojis = {
        'draw': ['🎨', '✏️', '🖌️', '🎭'],
        'fist': ['✊', '💪', '🥊', '👊'],
        'clear': ['🧹', '🗑️', '🔄', '✨'],
        'idle': ['⏸️', '😴', '🧘', '🌙']
    }
    emoji = random.choice(emojis.get(gesture, ['🤔']))
    print(f"{emoji} [PLAY] Gesture: {gesture.upper()} | Position: {cursor}")


def _log_clear(canvas: object, **kwargs) -> None:
    celebrations = ['🎉 Fresh start!', '✨ Clean canvas!', '🧹 All clear!', '🔄 New beginning!']
    print(f"[PLAY] {random.choice(celebrations)}")


def _log_draw(start: tuple[int, int], end: tuple[int, int], canvas: object, **kwargs) -> None:
    # Only log occasionally to avoid spam
    if random.random() < 0.1:  # 10% chance
        art_comments = ['Beautiful!', 'Nice stroke!', 'Artistic!', 'Creative!', 'Fantastic!']
        print(f"🎨 [PLAY] {random.choice(art_comments)} Drawing from {start} to {end}")


def _log_palette_selection(color: tuple[int, int, int], **kwargs) -> None:
    color_names = {
        (0, 255, 0): 'Green',
        (255, 0, 0): 'Blue',
        (0, 0, 255): 'Red',
        (255, 255, 0): 'Cyan',
        (255, 0, 255): 'Magenta',
        (0, 255, 255): 'Yellow',
        (255, 165, 0): 'Orange',
        (128, 0, 128): 'Purple',
        (255, 20, 147): 'Pink',
        (0, 191, 255): 'Sky Blue',
        (255, 255, 255): 'White',
        (0, 0, 0): 'Black'
    }
    color_name = color_names.get(color, f'RGB{color}')
    print(f"🎨 [PALETTE] Selected {color_name} color!")


def _log_start(**kwargs) -> None:
    print("🎮 [PLAY] Air Canvas with Color Palette Started! Point at colors to select, then draw! 🎨✨")


def _log_exit(**kwargs) -> None:
    print("👋 [PLAY] Thanks for creating art! Come back soon! 🎨")


hooks.register("gesture", _log_gesture)
hooks.register("clear", _log_clear)
hooks.register("draw", _log_draw)
hooks.register("palette_select", _log_palette_selection)
hooks.register("start", _log_start)
hooks.register("exit", _log_exit)
