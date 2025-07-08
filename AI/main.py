import cv2
from ultralytics import YOLO
import numpy as np

cap = cv2.VideoCapture(0)

# need to train your model
model = YOLO("yolov8m.pt")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break
    
    results = model(frame)
    results = results[0]
    box = np.array(results.boxes.xyxy.cpu(), dtype=int)
  
    # box the object
    for box_print in box:
        (x, y, x2, y2) = box_print
        cv2.rectangle(frame, (x,y), (x2, y2), (0, 0, 255), 3)
    
    cv2.imshow('Img', frame)
    key = cv2.waitKey(1)

    if key == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
    
