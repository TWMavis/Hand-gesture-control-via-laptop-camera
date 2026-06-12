"""HandControl 可調參數。距離類參數皆為「以手掌大小正規化」後的比例值。"""

# --- 攝影機 ---
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# --- 模型 ---
MODEL_PATH = "models/hand_landmarker.task"

# --- 捏合(遲滯:進入閾值 < 離開閾值,避免邊界抖動連點)---
PINCH_ENTER = 0.30   # 指尖距離/手掌大小 低於此值 → 視為捏合
PINCH_EXIT = 0.42    # 高於此值 → 視為放開
CLICK_MAX_DURATION = 0.30  # 捏合短於此秒數=點擊,超過=拖曳

# --- 游標 ---
ACTIVE_REGION = 0.60     # 畫面中央此比例的區域映射到整個螢幕
SMOOTHING_ALPHA = 0.35   # EMA 平滑係數(越小越平滑、越大越跟手)
DEAD_ZONE_PX = 2         # 小於此像素的移動忽略(消除手抖)

# --- 捲動 ---
SCROLL_SENSITIVITY = 25.0  # 正規化垂直移動量 → 滾輪格數的倍率
SCROLL_DEAD_ZONE = 0.005   # 小於此移動量不捲動

# --- 手掌左滑(上一頁)---
SWIPE_SPEED_THRESHOLD = 1.0  # 手掌水平速度(畫面寬/秒),向左超過即觸發
SWIPE_COOLDOWN = 1.0         # 觸發後冷卻秒數

# --- 偵測信心度 ---
MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.5
