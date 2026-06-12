"""MediaPipe HandLandmarker 包裝(Tasks API,mediapipe >= 0.10.30 已無 solutions API)。

輸入一幀 RGB 影像,回傳 21 個手部關鍵點的正規化座標(0~1),沒偵測到手則回傳 None。
"""

import urllib.request
from pathlib import Path

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

import config

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

# 關鍵點索引(MediaPipe 定義)
WRIST = 0
THUMB_TIP = 4
INDEX_PIP = 6
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_TIP = 12
RING_PIP = 14
RING_TIP = 16
PINKY_PIP = 18
PINKY_TIP = 20

# 骨架連線(畫預覽用)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # 拇指
    (0, 5), (5, 6), (6, 7), (7, 8),          # 食指
    (5, 9), (9, 10), (10, 11), (11, 12),     # 中指
    (9, 13), (13, 14), (14, 15), (15, 16),   # 無名指
    (13, 17), (17, 18), (18, 19), (19, 20),  # 小指
    (0, 17),                                  # 掌緣
]


class HandTracker:
    def __init__(self, model_path: str = config.MODEL_PATH):
        path = Path(model_path)
        if not path.exists():
            print(f"模型不存在,下載中: {MODEL_URL}")
            path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(MODEL_URL, path)

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._last_ts = -1

    def process(self, frame_rgb, timestamp_ms: int):
        """偵測一幀。回傳 21 個 landmark 或 None。

        detect_for_video 要求時間戳嚴格遞增,同一毫秒內的連續幀會自動往後推 1ms。
        """
        timestamp_ms = max(timestamp_ms, self._last_ts + 1)
        self._last_ts = timestamp_ms
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if result.hand_landmarks:
            return result.hand_landmarks[0]
        return None

    def close(self):
        self._landmarker.close()
