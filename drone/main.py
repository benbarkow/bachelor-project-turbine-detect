from drone import Drone
from yolov8 import ObjectDetection
import cv2


drone = Drone()

frame_width = 640
frame_height = 480
drone_done = False

target_size = 100

drone.home()
print("homing done!")
detector = ObjectDetection(capture_index=1)
print("detector initialized")
curr_dir_x = 0
center_x = False
curr_dir_y = 0
while not drone_done:
	center, size = detector.detect()
	# print(center)
	if cv2.waitKey(5) & 0xFF == ord('q'):
		break

	if center is not None and not center_x:
		if center[0] > frame_width/2 - 10 and center[0] < frame_width/2 + 10:
			if curr_dir_x == 0:
				print("centered", center[0])
				center_x = True
				continue
			curr_dir_x = 0
			drone.stop()
		elif center[0] < frame_width/2 - 11:
			if curr_dir_x == -1:
				continue
			curr_dir_x = -1
			drone.moveDir('x', -1, 50)
		elif center[0] > frame_width/2 + 11:
			if curr_dir_x == 1:
				continue
			curr_dir_x = 1
			drone.moveDir('x', 1, 50)

	if size is not None and center_x:
		if size > target_size - 10 and size < target_size + 10:
			if curr_dir_y == 0:
				print("target reached", center[0])
				center_x = False
				continue
			curr_dir_y = 0
			drone.stop()
		elif size < target_size - 11:
			if curr_dir_y == -1:
				continue
			curr_dir_y = -1
			drone.moveDir('y', -1, 50)
		elif size > target_size + 11:
			if curr_dir_y == 1:
				continue
			curr_dir_y = 1
			drone.moveDir('y', 1, 50) 			

detector.close()

