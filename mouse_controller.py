"""pynput 包裝:游標映射與平滑、點擊、拖曳、捲動、上一頁快捷鍵。"""

import ctypes

from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Button, Controller as MouseController

import config


def _screen_size():
    user32 = ctypes.windll.user32
    try:
        # 宣告 DPI awareness,讓回傳的是實體像素而非縮放後的虛擬尺寸
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except OSError:
        user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


class CursorController:
    def __init__(self):
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
        self._screen_w, self._screen_h = _screen_size()
        self._smooth_x = None
        self._smooth_y = None
        self._dragging = False

    # --- 游標移動 ---

    def move_to_normalized(self, nx: float, ny: float):
        """輸入鏡像畫面中的正規化座標(0~1),映射活動區域到全螢幕並平滑移動。"""
        margin = (1.0 - config.ACTIVE_REGION) / 2.0
        mapped_x = (nx - margin) / config.ACTIVE_REGION
        mapped_y = (ny - margin) / config.ACTIVE_REGION
        mapped_x = min(max(mapped_x, 0.0), 1.0)
        mapped_y = min(max(mapped_y, 0.0), 1.0)

        target_x = mapped_x * (self._screen_w - 1)
        target_y = mapped_y * (self._screen_h - 1)

        if self._smooth_x is None:
            self._smooth_x, self._smooth_y = target_x, target_y
        else:
            a = config.SMOOTHING_ALPHA
            self._smooth_x += a * (target_x - self._smooth_x)
            self._smooth_y += a * (target_y - self._smooth_y)

        cur_x, cur_y = self._mouse.position
        if (abs(self._smooth_x - cur_x) > config.DEAD_ZONE_PX
                or abs(self._smooth_y - cur_y) > config.DEAD_ZONE_PX):
            self._mouse.position = (int(self._smooth_x), int(self._smooth_y))

    def reset_smoothing(self):
        """手離開畫面或游標解鎖時呼叫,避免游標跳到舊位置。"""
        self._smooth_x = None
        self._smooth_y = None

    # --- 點擊與拖曳 ---

    def left_click(self):
        self._mouse.click(Button.left)

    def right_click(self):
        self._mouse.click(Button.right)

    def drag_start(self):
        if not self._dragging:
            self._mouse.press(Button.left)
            self._dragging = True

    def drag_end(self):
        if self._dragging:
            self._mouse.release(Button.left)
            self._dragging = False

    # --- 捲動 ---

    def scroll(self, amount: float):
        """amount 為滾輪格數,正值向上。"""
        if amount:
            self._mouse.scroll(0, amount)

    # --- 上一頁 ---

    def browser_back(self):
        with self._keyboard.pressed(Key.alt):
            self._keyboard.press(Key.left)
            self._keyboard.release(Key.left)

    def release_all(self):
        """程式結束或暫停時呼叫,確保不殘留按住狀態。"""
        self.drag_end()
        self.reset_smoothing()
