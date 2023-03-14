import cv2
import numpy as np
import time

#sample video 
cap = cv2.VideoCapture(1)
#set width and height
cap.set(3, 640)	
cap.set(4, 480)

begin = time.time()
count = 1
while cap.isOpened() and count < 200:
	ret, frame = cap.read()
	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	if count * 1/10 > time.time() - begin:
		continue
	if not ret:
		print("Can't receive frame (stream end?). Exiting ...")
		break
	#export frame to image
	cv2.imwrite('drone/data/yolov8_custom/{}.jpg'.format(str(count).zfill(6)), frame)
	cv2.waitKey(0)
	count += 1

cap.release()
cv2.destroyAllWindows()


		
