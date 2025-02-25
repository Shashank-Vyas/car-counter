from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *


cap = cv2.VideoCapture("car1.mp4")
cap.set(3, 640)
cap.set(4, 480)


model = YOLO("../Yolo weights/yolov8l.pt")

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "potted plant", "bed", "dining table", "toilet", "tv monitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]

mask = cv2.imread("Mask.png")
imgGraphics = cv2.imread("count.png")

# tracking
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

limits = [505, 423, 1115, 423]
totalCount = []

while True:
    success, frame = cap.read()
    imgRegion = cv2.bitwise_and(frame, mask)

    imgGraphics = cv2.imread("count.png", cv2.IMREAD_UNCHANGED)
    frame = cvzone.overlayPNG(frame, imgGraphics, (0, 0))

    results = model(imgRegion, stream=True)

    detections = np.empty((0, 5))
    for r in results:
        boxes = r.boxes
        for box in boxes:

            # Bounding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            w, h = x2-x1, y2-y1
            
            # Confidence
            conf = math.ceil((box.conf[0]*100))/100
            print(conf)
            # Class Name
            cls = int(box.cls[0])
            # 
            # 
            # New Code



            currentClass = classNames[cls]

            if currentClass == "car" or currentClass == "truck" or currentClass == "motorbike" or currentClass == "bus" and conf > 0.4:
                # cvzone.putTextRect(img, f'{currentClass}' f'{conf}', (max(0, x1),max(35, y1)), scale=0.6, thickness=1, offset=3)
                # cvzone.cornerRect(img,(x1, y1, w, h), l=10, rt=5)
                currentArray = np.array([x1, y1, x2, y2, conf])
                detections = np.vstack((detections, currentArray))


    resultsTracker = tracker.update(detections)
    cv2.line(frame, (limits[0], limits[1]), (limits[2], limits[3]), (0, 0, 255), 4)

    for result in resultsTracker:
        x1, y1, x2, y2, id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        print(result)
        w, h = x2-x1, y2-y1
        cvzone.cornerRect(frame,(x1, y1, w, h), l=12, rt=2, colorR=(255, 0, 255))
        cvzone.putTextRect(frame,f'{int(id)}', (max(0, x1),max(35, y1)), scale=2, thickness=3, offset=10)

        cx, cy = x1+w//2, y1+h//2
        cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        if limits[0]< cx <limits[2] and limits[1] - 20 < cy <limits[1] + 20:
            if totalCount.count(id) == 0:
                totalCount.append(id)
                cv2.line(frame, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 4)
    # cvzone.putTextRect(img, f'Count: {len(totalCount)}', (50,50))
    cv2.putText(frame, str(len(totalCount)), (410, 110), cv2.FONT_HERSHEY_PLAIN, 5, (50, 50, 255), 8)
            # 
            # 
            # 

    cv2.imshow("Image", frame)
    # cv2.imshow("ImageRegion", imgRegion)
    if cv2.waitKey(1) & 0XFF == ord('1'):
        break