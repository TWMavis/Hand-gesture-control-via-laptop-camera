"""HandControl 主程式:攝影機 → 手部追蹤 → 手勢狀態機 → 滑鼠控制 + 預覽視窗。

操作:ESC 結束,空白鍵 暫停/恢復控制。
"""

import os

# 關閉 MediaPipe/TensorFlow 的內部雜訊(含無害的遙測上傳失敗訊息),
# 必須在 import mediapipe 之前設定
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "3")

import time

import cv2

import config
from gestures import GestureEngine
from hand_tracker import HAND_CONNECTIONS, HandTracker
from mouse_controller import CursorController

STATE_COLORS = {
    "LOST": (128, 128, 128),
    "IDLE": (200, 200, 200),
    "MOVE": (0, 255, 0),
    "PINCH": (0, 200, 255),
    "DRAG": (0, 100, 255),
    "SCROLL": (255, 200, 0),
    "PALM": (255, 0, 200),
    "SWIPE": (0, 0, 255),
}


def draw_overlay(frame, landmarks, state, fps, paused):
    h, w = frame.shape[:2]
    color = STATE_COLORS.get(state, (255, 255, 255))

    # 活動區域框(手在框內即可到達整個螢幕)
    margin = (1.0 - config.ACTIVE_REGION) / 2.0
    cv2.rectangle(
        frame,
        (int(margin * w), int(margin * h)),
        (int((1 - margin) * w), int((1 - margin) * h)),
        (80, 80, 80), 1,
    )

    # 手部骨架
    if landmarks is not None:
        pts = [(int(p.x * w), int(p.y * h)) for p in landmarks]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], color, 2)
        for p in pts:
            cv2.circle(frame, p, 3, (255, 255, 255), -1)

    # 狀態文字
    cv2.putText(frame, f"{state}  FPS:{fps:.0f}", (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    if paused:
        cv2.putText(frame, "PAUSED (space to resume)", (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, "ESC: quit  SPACE: pause", (10, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)


def open_camera():
    """依序嘗試各後端開啟攝影機(部分機器只支援其中一種)。"""
    for backend in (cv2.CAP_MSMF, cv2.CAP_ANY, cv2.CAP_DSHOW):
        cap = cv2.VideoCapture(config.CAMERA_INDEX, backend)
        if cap.isOpened():
            ok, frame = cap.read()
            if ok and frame is not None:
                return cap
        cap.release()
    return None


def main():
    cap = open_camera()
    if cap is None:
        print(f"無法開啟攝影機(index={config.CAMERA_INDEX}),請確認沒被其他程式占用,"
              f"或修改 config.py 的 CAMERA_INDEX,也可執行 camera_probe.py 掃描可用攝影機")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    tracker = HandTracker()
    engine = GestureEngine()
    mouse = CursorController()

    paused = False
    fps = 0.0
    t0 = time.monotonic()
    prev_frame_t = t0

    print("HandControl 啟動。ESC 結束,空白鍵暫停/恢復。")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("讀不到攝影機畫面,結束。")
                break

            frame = cv2.flip(frame, 1)  # 鏡像,左右移動才符合直覺
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            now = time.monotonic()
            landmarks = tracker.process(rgb, int((now - t0) * 1000))
            out = engine.update(landmarks, now)

            if not paused:
                for ev in out.events:
                    kind = ev[0]
                    if kind == "left_click":
                        mouse.left_click()
                    elif kind == "right_click":
                        mouse.right_click()
                    elif kind == "drag_start":
                        mouse.drag_start()
                    elif kind == "drag_end":
                        mouse.drag_end()
                    elif kind == "scroll":
                        mouse.scroll(ev[1])
                    elif kind == "back":
                        mouse.browser_back()
                if out.cursor is not None:
                    mouse.move_to_normalized(*out.cursor)

            if landmarks is None:
                mouse.reset_smoothing()

            dt = now - prev_frame_t
            prev_frame_t = now
            if dt > 0:
                fps = fps * 0.9 + (1.0 / dt) * 0.1

            draw_overlay(frame, landmarks, out.state, fps, paused)
            cv2.imshow("HandControl", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            if key == 32:  # 空白鍵
                paused = not paused
                mouse.release_all()
    finally:
        mouse.release_all()
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
