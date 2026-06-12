"""掃描可用攝影機:測試 index 0~3 搭配 MSMF / DSHOW / 預設後端,印出可讀取畫面的組合。"""

import cv2

BACKENDS = [
    ("MSMF", cv2.CAP_MSMF),
    ("DSHOW", cv2.CAP_DSHOW),
    ("ANY", cv2.CAP_ANY),
]

found = []
for name, backend in BACKENDS:
    for idx in range(4):
        cap = cv2.VideoCapture(idx, backend)
        if cap.isOpened():
            ok, frame = cap.read()
            if ok and frame is not None:
                h, w = frame.shape[:2]
                print(f"OK  index={idx} backend={name} {w}x{h}")
                found.append((idx, name))
            else:
                print(f"OPENED-BUT-NO-FRAME  index={idx} backend={name}")
        cap.release()

if not found:
    print("找不到可用攝影機。請檢查 Windows 設定 > 隱私權與安全性 > 攝影機,"
          "確認允許桌面應用程式存取攝影機,且沒有其他程式占用。")
