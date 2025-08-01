import cv2
from ultralytics import YOLO
import numpy as np

cap = cv2.VideoCapture(0)

# Load pretrained model (YOLOv8m on COCO)
model = YOLO("yolov8m.pt")

list_of_persons = []

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    results = model(frame)[0]  # Get the first batch result

    # Get boxes and class IDs
    boxes = results.boxes.xyxy.cpu().numpy().astype(int)
    class_ids = results.boxes.cls.cpu().numpy().astype(int)
    
    # Loop through detections
    list_of_persons.clear()
    for box, class_id in zip(boxes, class_ids):
        if class_id == 0:  # Class 0 = 'person' in COCO dataset
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 0, 255), 2)
            list_of_persons.append((x1+x2)/2)
            
    print("List of persons:", list_of_persons)

    cv2.imshow('Img', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
