import cv2

cap = cv2.VideoCapture('walkingGirl.mp4')  # 讀取影片檔案

while True:
    ret, frame = cap.read() # ret 是成功與否(True/False), frame 是當前畫面
    if not ret:
        break
        
    cv2.imshow("Video", frame) # 顯示視窗
    
    if cv2.waitKey(1) & 0xFF == ord('q'): # 按下 'q' 鍵退出
        break

cap.release() # 釋放鏡頭
cv2.destroyAllWindows() # 關閉所有視窗