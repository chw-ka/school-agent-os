"""
S3 CMP 第二學期 實習評估（2025-2026）
任務二：《物件追蹤》（禁止使用任何 AI 工具）

請完成下面的填空程式，令程式能做到：
- 開啟影片檔（例如：`tracking_video.mp4`）
- 在第一格畫面讓使用者選取要追蹤的物件（ROI）
- 使用追蹤器（MIL）追蹤物件
- 用紅色方框框住追蹤到的物件
- 左上角顯示追蹤器類型
- 按 ESC 退出
"""

# (a) 匯入函數庫
import

# (b) 設定 tracker 類型（本題用 MIL）
tracker_type = "MIL"

# (c) 根據 tracker_type 初始化追蹤器
if tracker_type == "BOOSTING":
    tracker = cv2.legacy.TrackerBoosting_create()
elif tracker_type == "MIL":
    tracker = cv2.legacy.TrackerMIL_create()
elif tracker_type == "KCF":
    tracker = cv2.legacy.TrackerKCF_create()
elif tracker_type == "CSRT":
    tracker = cv2.legacy.TrackerCSRT_create()
else:
    raise ValueError("不支援的 tracker 類型")

# (d) 開啟影片檔 + 讀取第一格畫面
video = cv2.
isTrue, frame =
if not isTrue:
    raise RuntimeError("無法從影片讀取畫面")

# (e) 選取 ROI + 初始化 tracker
bbox = cv2.
ok = tracker.
if not ok:
    raise RuntimeError("Tracker 初始化失敗")

colors = (0, 0, 255)  # BGR red

while True:
    isTrue, frame = video.
    if not isTrue:
        break

    # (f) 更新 tracker
    ok, bbox = tracker.
    if ok:
        (x, y, w, h) = [int(v) for v in bbox]
        # (g) 畫出矩形框
        cv2.

    # 顯示 tracker 類型
    cv2.putText(frame, tracker_type, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors, 2)

    # (h) 顯示影像
    cv2.

    # 按 ESC 退出
    if cv2.waitKey(1) & 0xFF == 27:
        break

video.release()
cv2.destroyAllWindows()

