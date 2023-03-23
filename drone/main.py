from drone import Drone
from yolov8 import ObjectDetection

detector = ObjectDetection(capture_index=1)

drone = Drone()

frame_width = 640
frame_height = 480
drone_done = False

drone.home()
print("homing done!")

while not drone_done:
	center = detector()
	if center is not None:
		print(center)
		if center[0] < frame_width/2 - 50:
			drone.moveDir('x', -1)
		elif center[0] > frame_width/2 + 50:
			drone.moveDir('x', 1)
		else:
			drone.stop()
			drone_done = True

