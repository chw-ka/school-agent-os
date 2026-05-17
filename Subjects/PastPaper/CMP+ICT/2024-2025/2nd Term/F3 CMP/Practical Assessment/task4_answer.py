# task4_2425.py

# Step (b): Import the OpenCV library
import cv2

# Step (c): Load the video
cap = cv2.VideoCapture("video.mp4")

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    # Step (d): Read frames from the video
    isTrue, frame = cap.read()
    if not isTrue:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Step (e): Use a rectangle to mark detected faces in each frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.25, minNeighbors=10)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Step (f): Display the video with marked faces
    cv2.imshow('Video', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()