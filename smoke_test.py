"""煙霧測試:不開攝影機與視窗,驗證模型初始化與整條管線可以執行。"""

import numpy as np

from gestures import GestureEngine
from hand_tracker import HandTracker
from mouse_controller import CursorController

tracker = HandTracker()
engine = GestureEngine()

frame = np.zeros((480, 640, 3), dtype=np.uint8)
lm = tracker.process(frame, 0)
out = engine.update(lm, 0.0)
print("tracker OK, state =", out.state)

mouse = CursorController()
print("screen =", mouse._screen_w, "x", mouse._screen_h)
print("smoke test PASS")
