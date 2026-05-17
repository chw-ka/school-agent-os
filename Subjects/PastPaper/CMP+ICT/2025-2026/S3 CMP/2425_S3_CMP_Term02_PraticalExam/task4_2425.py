# part (b) line 2
import

# part (c) line 5
face_cascade = cv.

# part (d) line 8
video = cv.

while True:
    # part (e) line 12 - 14
    isTrue, frame =
    if
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        center_x, center_y = x + w // 2, y + h // 2
        cv2.circle(frame, (center_x, center_y), 10, (0, 255, 0), 2)

    # part (f) line 26
    cv2.

    # part (g) line 29
    cv2.