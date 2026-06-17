# part (b) line 2
import cv2

# part (c) line 5
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# part (d) line 8
video = cv2.VideoCapture("video.mp4")

while True:
    # part (e) line 12 - 14
    isTrue, frame = video.read()
    if not isTrue:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        center_x, center_y = x + w // 2, y + h // 2
        cv2.circle(frame, (center_x, center_y), 10, (0, 255, 0), 2)

    # part (f) line 26
    cv2.imshow("Video", frame)

    # part (g) line 29
    cv2.waitKey(1)