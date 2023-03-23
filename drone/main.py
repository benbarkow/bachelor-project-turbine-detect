from drone import Drone
from yolov8 import ObjectDetection
import cv2

def main():
	drone = Drone()

	frame_width = 640
	frame_height = 480
	drone_done = False

	target_size = 200

	drone.home()
	print("homing done!")

	detector = ObjectDetection(capture_index=1)

	# while True:
	# 	center, size = detector.detect()
	# 	print(center, size)
	# 	if cv2.waitKey(5) & 0xFF == ord('q'):
	# 		break
	# return 

	print("detector initialized")
	curr_dir_x = 0
	x_done = False
	y_done = False
	curr_dir_y = 0
	mode = "x"
	move = True
	while not drone_done:
		center, size = detector.detect()
		# print(center)
		if cv2.waitKey(3) & 0xFF == ord('q'):
			break

		if size > target_size + 10:
			mode = "y"
		
		prev_mode = mode

		delta_y = abs(target_size - size)
		y_speed = max(10, min(int(delta_y), 100))
		x_speed = max(20, min(int(delta_y), 50))

		if center is not None and mode == "x":
			mode_done = False
			if center[0] > frame_width/2 - 10 and center[0] < frame_width/2 + 10:
				if curr_dir_x == 0:
					mode = "y"
				curr_dir_x = 0
				drone.stop('x')
				drone.stop('y')
			elif center[0] < frame_width/2 - 11:
				if curr_dir_x == -1:
					continue
				curr_dir_x = -1
				drone.moveDir('x', -1, x_speed)
			elif center[0] > frame_width/2 + 11:
				if curr_dir_x == 1:
					continue
				curr_dir_x = 1
				drone.moveDir('x', 1, x_speed)
		else:
			if size is not None and mode == "y":
				print("curr_dir_y", curr_dir_y)
				if size > target_size - 10 and size < target_size + 10:
					if curr_dir_y == 0:
						mode = "x"
					curr_dir_y = 0
					drone.stop('x')
					drone.stop('y')
				elif size < target_size - 11:
					if curr_dir_y > 0:
						y_speed_delta = curr_dir_y - y_speed
						print("y_speed_delta", y_speed_delta)
						if y_speed_delta > 10:
							drone.moveDir('y', 1, y_speed) 			
							curr_dir_y = y_speed
						continue
					curr_dir_y = y_speed
					drone.moveDir('y', 1, y_speed) 			
				elif size > target_size + 11:
					if curr_dir_y < 0:
						y_speed_delta = curr_dir_y + y_speed
						print("y_speed_delta", y_speed_delta)
						if y_speed_delta < -10:
							drone.moveDir('y', -1, y_speed) 			
							curr_dir_y = -y_speed
						continue
					curr_dir_y = -y_speed
					drone.moveDir('y', -1, y_speed)
		if prev_mode != mode:
			if mode == "y" and size > target_size - 10 and size < target_size + 10:
				input("Press Enter to continue...")
			if mode == "x" and center[0] > frame_width/2 - 10 and center[0] < frame_width/2 + 10:
				input("Press Enter to continue...")

	detector.close()


if __name__ == '__main__':
	main()

