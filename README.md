# HandControl

用筆電攝影機偵測手勢來操控滑鼠,像一個隔空的觸控板。

## 安裝

需要 Python 3.9–3.12(MediaPipe 不支援 3.13+)。本專案使用 [uv](https://docs.astral.sh/uv/) 管理:

```powershell
uv venv --python 3.12 .venv
uv pip install -r requirements.txt --python .venv
```

(或用一般 pip:`python -m venv .venv`、`.venv\Scripts\pip install -r requirements.txt`)

手部追蹤模型 `models/hand_landmarker.task` 第一次執行時會自動下載。

## 執行

雙擊 `HandControl.bat` 即可啟動,或在終端機執行:

```powershell
.venv\Scripts\python.exe main.py
```

- `空白鍵`:暫停/恢復控制(緊急停用)
- `ESC`:結束程式

把手放在預覽視窗的灰色框內,手在框內移動即可到達整個螢幕。

## 手勢

| 手勢 | 動作 |
|---|---|
| 🖐️ 移動手掌(掌心位置) | 移動游標 |
| ✊ 握拳 | 游標停住(像手指離開觸控板,可重新定位) |
| 🤏 拇指+食指快速捏放 | 左鍵點擊 |
| 🤏 拇指+食指捏住不放 | 拖曳(放開即鬆手) |
| 拇指+中指捏合 | 右鍵點擊 |
| ✌️ 食指+中指伸直上下移動 | 捲動 |
| 🖐️ 手掌張開快速向左滑 | 上一頁(Alt+←) |

## 調整

所有靈敏度、閾值都在 [config.py](config.py),常用的:

- 游標太抖 → 調低 `SMOOTHING_ALPHA`
- 點擊不靈敏 → 調高 `PINCH_ENTER`
- 手要移很遠 → 調低 `ACTIVE_REGION`
- 攝影機開不起來 → 執行 `camera_probe.py` 掃描,修改 `CAMERA_INDEX`

## 疑難排解

- **攝影機無法開啟**:檢查 Windows 設定 → 隱私權與安全性 → 攝影機,允許桌面應用程式存取;確認沒有其他程式(視訊會議等)占用。
- **環境驗證**:`.venv\Scripts\python.exe smoke_test.py` 可在不開攝影機的情況下測試整條管線。

更多架構說明見 [overview.md](overview.md)。
