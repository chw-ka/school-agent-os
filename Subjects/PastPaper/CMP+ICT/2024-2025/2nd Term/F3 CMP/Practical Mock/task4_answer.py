# part (b) line 2
import cv2

# Main menu
print("Choose a mode:")
print("1. Image")
print("2. Video")

mode = input("Enter 1 or 2: ")

if mode == "1":
    # part (c) line 13 - 15
    image = cv2.imread("face.jpg")
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    
elif mode == "2":
    # part (d) line 19 - 25
    cap = cv2.VideoCapture("video.mp4")
    while True:
        isTrue, frame = cap.read()
        if not isTrue:
            break
        cv2.imshow("Video", frame)
        cv2.waitKey(1)
        
# This is a program that allows the user to choose between displaying an image or a video.