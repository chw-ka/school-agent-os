import cv2

# 1. 載入人臉識別模型 (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 2. 讀取圖片
img = cv2.imread('input.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 轉為灰階

# 3. 偵測臉部（提高 minNeighbors 減少誤判；minSize 過濾遠處小臉）
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1, minSize=(10, 10))

# 4. 繪製紅色方框 (BGR: 0, 0, 255)
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)

# 5. 顯示結果
cv2.imshow('Face Detection', img)
cv2.waitKey(0) # 按下任意鍵關閉視窗