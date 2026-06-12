"""手勢狀態機:輸入 21 個手部關鍵點,輸出目前狀態、游標目標與動作事件。

事件格式:
    ("left_click",) ("right_click",) ("drag_start",) ("drag_end",)
    ("scroll", 格數) ("back",)
"""

import math
from dataclasses import dataclass, field

import config
from hand_tracker import (
    WRIST, THUMB_TIP,
    INDEX_PIP, INDEX_TIP,
    MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP,
    RING_PIP, RING_TIP,
    PINKY_PIP, PINKY_TIP,
)


def _dist(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


@dataclass
class GestureOutput:
    state: str                      # LOST / IDLE / MOVE / PINCH / DRAG / SCROLL / PALM / SWIPE
    cursor: tuple | None = None     # 正規化座標,None = 游標鎖定不動
    events: list = field(default_factory=list)


class GestureEngine:
    def __init__(self):
        self._pinch_active = False
        self._pinch_start_t = 0.0
        self._dragging = False
        self._right_armed = True
        self._scroll_prev_y = None
        self._prev_palm_x = None
        self._prev_t = None
        self._swipe_ready_t = 0.0

    def update(self, lm, t: float) -> GestureOutput:
        events = []

        if lm is None:
            if self._dragging:
                events.append(("drag_end",))
                self._dragging = False
            self._pinch_active = False
            self._scroll_prev_y = None
            self._prev_palm_x = None
            return GestureOutput("LOST", None, events)

        # 手掌大小(手腕到中指根部)作為所有距離的正規化基準
        palm = _dist(lm[WRIST], lm[MIDDLE_MCP])
        if palm < 1e-6:
            return GestureOutput("LOST", None, events)

        pinch_index = _dist(lm[THUMB_TIP], lm[INDEX_TIP]) / palm
        pinch_middle = _dist(lm[THUMB_TIP], lm[MIDDLE_TIP]) / palm

        # 游標跟隨手掌心(手腕與中指根部的中點),比指尖穩定
        palm_cursor = (
            (lm[WRIST].x + lm[MIDDLE_MCP].x) / 2.0,
            (lm[WRIST].y + lm[MIDDLE_MCP].y) / 2.0,
        )

        # 手指是否伸直:指尖離手腕比第二關節(PIP)遠
        def extended(tip, pip):
            return _dist(lm[tip], lm[WRIST]) > _dist(lm[pip], lm[WRIST])

        index_ext = extended(INDEX_TIP, INDEX_PIP)
        middle_ext = extended(MIDDLE_TIP, MIDDLE_PIP)
        ring_ext = extended(RING_TIP, RING_PIP)
        pinky_ext = extended(PINKY_TIP, PINKY_PIP)

        # 手掌水平速度(畫面寬/秒),用於左滑偵測
        palm_x = lm[MIDDLE_MCP].x
        vx = 0.0
        if self._prev_palm_x is not None and t > self._prev_t:
            vx = (palm_x - self._prev_palm_x) / (t - self._prev_t)
        self._prev_palm_x = palm_x
        self._prev_t = t

        # --- 1. 拇指+食指捏合:點擊 / 拖曳(遲滯判定)---
        if self._pinch_active:
            if pinch_index > config.PINCH_EXIT:
                self._pinch_active = False
                if self._dragging:
                    events.append(("drag_end",))
                    self._dragging = False
                elif t - self._pinch_start_t <= config.CLICK_MAX_DURATION:
                    events.append(("left_click",))
                return GestureOutput("IDLE", None, events)
            if not self._dragging and t - self._pinch_start_t > config.CLICK_MAX_DURATION:
                events.append(("drag_start",))
                self._dragging = True
            if self._dragging:
                return GestureOutput("DRAG", palm_cursor, events)
            # 尚未確定是點擊還是拖曳:鎖定游標避免點擊瞬間飄移
            return GestureOutput("PINCH", None, events)

        if pinch_index < config.PINCH_ENTER:
            self._pinch_active = True
            self._pinch_start_t = t
            self._scroll_prev_y = None
            return GestureOutput("PINCH", None, events)

        # --- 2. 拇指+中指捏合:右鍵(需重新張開才能再次觸發)---
        if pinch_middle < config.PINCH_ENTER and pinch_index > config.PINCH_EXIT:
            if self._right_armed:
                events.append(("right_click",))
                self._right_armed = False
            return GestureOutput("PINCH", None, events)
        if pinch_middle > config.PINCH_EXIT:
            self._right_armed = True

        # --- 3. 手掌張開(四指伸直):移動游標,快速左滑=上一頁 ---
        if index_ext and middle_ext and ring_ext and pinky_ext:
            self._scroll_prev_y = None
            if vx < -config.SWIPE_SPEED_THRESHOLD and t >= self._swipe_ready_t:
                self._swipe_ready_t = t + config.SWIPE_COOLDOWN
                events.append(("back",))
                return GestureOutput("SWIPE", None, events)
            return GestureOutput("MOVE", palm_cursor, events)

        # --- 4. 食指+中指伸直、無名指小指收起:捲動 ---
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            y = (lm[INDEX_TIP].y + lm[MIDDLE_TIP].y) / 2.0
            if self._scroll_prev_y is not None:
                dy = y - self._scroll_prev_y
                if abs(dy) > config.SCROLL_DEAD_ZONE:
                    # 手往上移(dy<0)→ 頁面向上捲
                    events.append(("scroll", -dy * config.SCROLL_SENSITIVITY))
            self._scroll_prev_y = y
            return GestureOutput("SCROLL", None, events)
        self._scroll_prev_y = None

        # --- 5. 其他姿勢:手掌心移動游標;握拳=游標停住(像手指離開觸控板)---
        if index_ext or middle_ext or ring_ext or pinky_ext:
            return GestureOutput("MOVE", palm_cursor, events)

        return GestureOutput("IDLE", None, events)
