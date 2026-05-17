import cv2

# 1. 載入預訓練的人臉模型 (Haar Cascade)
# 這是 OpenCV 內建的檔案路徑，確保電腦能找到人臉特徵
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 2. 開啟預設鏡頭 
cap = cv2.VideoCapture("walkingGirl.mp4")

print("正在開啟影片... 按下 'q' 鍵可退出程式。")

while True:
    # 讀取鏡頭的每一幀 (Frame)
    ret, frame = cap.read()
    
    if not ret:
        print("無法讀取影片幀，請檢查設備連接。")
        break

    # 3. 轉換為灰階 (Gray Scale) 以提高識別效率
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 4. 偵測臉部
    # scaleFactor: 縮放比例, minNeighbors: 檢測多少次才確定是臉
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(100, 100))

    # 5. 處理偵測到的每一張臉
    for (x, y, w, h) in faces:
        # A. 擷取臉部區域 (Region of Interest, ROI)
        face_roi = frame[y:y+h, x:x+w]

        # B. 進行高斯模糊 (Gaussian Blur)
        # (99, 99) 是模糊核心大小，必須是奇數，數字越大越模糊
        blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 30)

        # C. 將處理後的模糊區域放回原圖
        frame[y:y+h, x:x+w] = blurred_face
        
        # (選做) 可以在模糊區外面畫一個圈，提醒學生這裡被偵測到了
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 1)

    # 6. 在畫面上加上文字標籤 (進階挑戰要求)
    # 參數：圖片, 文字, 位置, 字體, 大小, 顏色(BGR), 厚度
    cv2.putText(frame, "Privacy Mode: ON", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 7. 顯示結果視窗
    cv2.imshow('Smart Privacy Guard', frame)

    # 8. 偵測鍵盤按鍵，若按下 'q' 則離開迴圈
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 9. 釋放資源與關閉視窗
cap.release()
cv2.destroyAllWindows()