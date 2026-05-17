# 導入函數庫
import cv2

# 建立一個列表儲存不同演算法 並建立一個變數儲存從列表中揀選的演算法
tracker_type = 'MIL'

# 根據選擇的演算法類型初始化追蹤器
if tracker_type == 'BOOSTING':
    tracker = cv2.legacy.TrackerBoosting_create()
elif tracker_type == 'MIL':
    tracker = cv2.legacy.TrackerMIL_create()
elif tracker_type == 'KCF':
    tracker = cv2.legacy.TrackerKCF_create()
elif tracker_type == 'TLD':
    tracker = cv2.legacy.TrackerTLD_create()
elif tracker_type == 'MEDIANFLOW':
    tracker = cv2.legacy.TrackerMedianFlow_create()
elif tracker_type == 'MOSSE':
    tracker = cv2.legacy.TrackerMOSSE_create()
elif tracker_type == 'CSRT':
    tracker = cv2.legacy.TrackerCSRT_create()

# 開啟影片檔案
video = cv2.VideoCapture(0)
isTrue, frame = video.read()

# 選擇要追蹤的物件 (ROI)
bbox = cv2.selectROI(frame) # region of interest

# 初始化追蹤器
ok = tracker.init(frame, bbox)

# 設定矩形框顏色 (紅色)
colors = (0, 0, 255) # RGB -> BGR

# 開始一個迴圈以追蹤
while True:
    isTrue, frame = video.read()
    if not isTrue:
        break

    # 更新追蹤器並在影片上畫出邊界框
    ok, bbox = tracker.update(frame)
    if ok == True:
        (x, y, w, h) = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), colors, 2)

    # 在畫面上顯示演算法類型 (左上角)
    cv2.putText(frame, tracker_type, (100, 20), cv2.FONT_HERSHEY_SIMPLEX, .75, (0, 0, 255))

    # 顯示結果影像
    cv2.imshow('Tracking', frame)

    # 按下 ESC 鍵退出
    if cv2.waitKey(1) & 0XFF == 27: # esc
        break