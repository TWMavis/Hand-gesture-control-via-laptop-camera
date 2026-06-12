# HandControl 專案總覽

透過筆電攝影機偵測手部動作來操控電腦的軟體。邏輯類似觸控板,但改用手指移動與捏合等手勢,不需碰觸任何硬體。

## 運作原理

```
攝影機畫面 ──> MediaPipe 手部追蹤 ──> 手勢狀態機 ──> 滑鼠/鍵盤控制
 (OpenCV)      (21 個手部關鍵點)      (gestures.py)     (pynput)
                                          │
                                          v
                                    預覽視窗(骨架 + 狀態顯示)
```

每一幀畫面流程:
1. OpenCV 讀取攝影機並水平翻轉(鏡像,符合直覺)
2. MediaPipe Hands 偵測出手部 21 個關鍵點的正規化座標
3. 手勢狀態機根據關鍵點之間的距離與移動速度,判斷目前手勢
4. 依手勢呼叫 pynput 移動游標、點擊、捲動或送出快捷鍵
5. 預覽視窗畫出骨架、活動區域框與目前狀態

## 手勢對照表

| 手勢 | 判斷條件 | 動作 |
|---|---|---|
| 移動游標 | 手掌心(手腕與中指根部中點)位置映射到螢幕 | 滑鼠移動 |
| 游標停住 | 握拳(四指皆收起) | 暫停移動,可重新定位(觸控板抬手) |
| 左鍵點擊 | 拇指+食指捏合後 0.3 秒內放開 | 左鍵 click |
| 拖曳 | 拇指+食指捏合持續超過 0.3 秒 | 按住左鍵,放開捏合即鬆開 |
| 右鍵 | 拇指+中指捏合 | 右鍵 click |
| 捲動 | 食指+中指同時伸直併攏,上下移動 | 滾輪捲動 |
| 上一頁 | 五指張開的手掌快速向左滑 | Alt+Left |

所有捏合距離都以「手掌大小」(手腕到中指根部的距離)正規化,手離鏡頭遠近不影響判斷。

## 防誤觸機制

- **遲滯(hysteresis)**:捏合的進入閾值小於離開閾值,避免在邊界抖動造成連點
- **捏合時鎖定游標**:點擊瞬間游標不會飄移
- **左滑冷卻時間**:觸發上一頁後 1 秒內不再觸發
- **模式互斥**:捲動模式下不移動游標

## 模組職責

| 檔案 | 職責 |
|---|---|
| `main.py` | 主迴圈:攝影機讀取 → 追蹤 → 手勢 → 控制,以及預覽視窗繪製 |
| `hand_tracker.py` | MediaPipe 包裝,輸入影像、輸出 21 個關鍵點座標 |
| `gestures.py` | 手勢狀態機,輸入關鍵點、輸出手勢事件(移動/點擊/拖曳/捲動/左滑) |
| `mouse_controller.py` | pynput 包裝:游標映射與平滑(EMA)、點擊、捲動、快捷鍵 |
| `config.py` | 所有可調參數 |

## 可調參數(config.py)

| 參數 | 說明 |
|---|---|
| `CAMERA_INDEX` | 攝影機編號(預設 0) |
| `PINCH_ENTER` / `PINCH_EXIT` | 捏合進入/離開閾值(遲滯) |
| `CLICK_MAX_DURATION` | 點擊與拖曳的時間分界(秒) |
| `SMOOTHING_ALPHA` | 游標平滑係數(越小越平滑但越遲鈍) |
| `ACTIVE_REGION` | 畫面中映射到螢幕的活動區域比例 |
| `SCROLL_SENSITIVITY` | 捲動靈敏度 |
| `SWIPE_SPEED_THRESHOLD` / `SWIPE_COOLDOWN` | 左滑速度閾值與冷卻時間 |

## 操作方式

- `python main.py` 啟動
- `空白鍵`:暫停/恢復控制(緊急停用)
- `ESC`:結束程式

## 輔助工具

| 檔案 | 用途 |
|---|---|
| `smoke_test.py` | 不開攝影機驗證模型與整條管線可執行 |
| `camera_probe.py` | 掃描可用的攝影機 index 與後端組合 |

## 技術備註

- mediapipe 0.10.30+ 已移除舊版 `solutions` API,本專案使用 Tasks API(`HandLandmarker`,VIDEO 模式)
- 模型檔 `models/hand_landmarker.task` 不存在時會自動下載
- 此機器攝影機僅支援 MSMF 後端(DSHOW 開不起來),`main.py` 會自動輪詢後端
- 查詢螢幕尺寸前需宣告 DPI awareness,否則拿到縮放後的虛擬尺寸,游標到不了螢幕邊角

## 開發進度

- [x] overview.md 專案總覽
- [x] requirements.txt + venv 環境(uv + Python 3.12)
- [x] hand_tracker.py:MediaPipe Tasks API 包裝
- [x] mouse_controller.py:食指控制游標(映射 + 平滑 + DPI)
- [x] gestures.py:捏合點擊
- [x] gestures.py:拖曳
- [x] gestures.py:右鍵
- [x] gestures.py:捲動
- [x] gestures.py:手掌左滑上一頁
- [x] 預覽視窗狀態顯示 + 暫停鍵
- [x] README.md
- [ ] 實際手勢調校(依使用手感微調 config.py 閾值)
