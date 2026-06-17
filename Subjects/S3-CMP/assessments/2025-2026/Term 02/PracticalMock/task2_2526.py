# (b) 匯入函數庫
import

# (c) 載入人臉模型
face_cascade = cv.

# (d) 開啟影片
video = cv.

while True:
    # (e) 讀取每一格
    isTrue, frame =
    if
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        center_x, center_y = x + w // 2, y + h // 2
        cv2.circle(frame, (center_x, center_y), 10, (0, 255, 0), 2)

    # (f) 顯示影片
    cv2.

    # (g) 等待按鍵
    cv2.
