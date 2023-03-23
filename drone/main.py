from drone import Drone
from yolov8 import ObjectDetection
import cv2


drone = Drone()

frame_width = 640
frame_height = 480
drone_done = False

drone.home()
print("homing done!")
detector = ObjectDetection(capture_index=1)
print("detector initialized")
curr_dir = 0
while not drone_done:
	center = detector.detect()
	# print(center)
	if cv2.waitKey(5) & 0xFF == ord('q'):
		break

	if center is not None:
		if center[0] > frame_width/2 - 10 and center[0] < frame_width/2 + 10:
			if curr_dir == 0:
				print("centered", center[0])
				continue
			curr_dir = 0
			drone.stop()
		elif center[0] < frame_width/2 - 11:
			if curr_dir == -1:
				continue
			curr_dir = -1
			drone.moveDir('x', -1, 100)
		elif center[0] > frame_width/2 + 11:
			if curr_dir == 1:
				continue
			curr_dir = 1
			drone.moveDir('x', 1, 100)

detector.close()

