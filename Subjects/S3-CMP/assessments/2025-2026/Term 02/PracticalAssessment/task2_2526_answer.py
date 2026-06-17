import cv2

tracker_type = "MIL"

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

video = cv2.VideoCapture("tracking_video.mp4")
isTrue, frame = video.read()
if not isTrue:
    raise RuntimeError("無法從影片讀取畫面")

bbox = cv2.selectROI(frame)
ok = tracker.init(frame, bbox)
if not ok:
    raise RuntimeError("Tracker 初始化失敗")

colors = (0, 0, 255)  # BGR red

while True:
    isTrue, frame = video.read()
    if not isTrue:
        break

    ok, bbox = tracker.update(frame)
    if ok:
        (x, y, w, h) = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), colors, 2)

    cv2.putText(frame, tracker_type, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors, 2)
    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

video.release()
cv2.destroyAllWindows()

