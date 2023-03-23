import torch
import numpy as np
import cv2
from time import time
from ultralytics import YOLO

from supervision.draw.color import ColorPalette
from supervision.tools.detections import Detections, BoxAnnotator


class ObjectDetection:

	def __init__(self, capture_index):
		
		self.capture_index = capture_index
		
		self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
		print("Using Device: ", self.device)
		
		self.model = self.load_model()

		self.center = None
		
		self.CLASS_NAMES_DICT = self.model.model.names
		self.CLASS_NAMES_DICT = {0: "blade"}

		self.box_annotator = BoxAnnotator(color=ColorPalette(), thickness=2, text_thickness=2, text_scale=0.5)

		self.cap = cv2.VideoCapture(self.capture_index)
		assert self.cap.isOpened()
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


	def load_model(self):
		
		model = YOLO("ml/yolov8_v02.pt")  # load a pretrained YOLOv8n model
		model.fuse()

		return model


	def predict(self, frame):
		
		results = self.model(frame)
		
		return results

	def get_turbine_center(self, results):
		min_edge = float('inf')
		boxes = []
		for result in results[0]:
			class_id = result.boxes.cls.cpu().numpy().astype(int)
			if class_id == 0:
				xyxy = result.boxes.xyxy.cpu().numpy()
				confidence = result.boxes.conf.cpu().numpy()[0]
				class_id = result.boxes.cls.cpu().numpy().astype(int)

				corners = np.array([[xyxy[0][0], xyxy[0][1]],
									[xyxy[0][2], xyxy[0][1]],
									[xyxy[0][2], xyxy[0][3]],
									[xyxy[0][0], xyxy[0][3]]])


				#for every corner find distance to every other corner
				# for i in range(4):
				# 	for box in boxes:
				# 		for j in range(4):
				# 			dist = np.linalg.norm(corners[i] - box[j])
				# 			for k in range(len(current_min_dists)):
				# 				if dist < current_min_dists[k]:
				# 					current_min_dists[k] = dist
				# 					current_min_dist_points[k] = [corners[i], box[j]]
				# 					break
				# 			if len(current_min_dists) <= 2:
				# 				current_min_dists.append(dist)
				# 				current_min_dist_points.append([corners[i], box[j]])

				#find the two corners that are closest to each other
				for i in range(4):
					for j in range(i+1, 4):
						edge = np.linalg.norm(corners[i] - corners[j])
						if edge < min_edge:
							min_edge = edge
				
				boxes.append(corners)
		#search for smallest circumfrence triangle with points from three different rectangle boxes
		if len(boxes) >= 3:
			min_circumfrence = float('inf')
			for i in range(len(boxes)):
				for j in range(i+1, len(boxes)):
					for k in range(j+1, len(boxes)):
						#permute all combinations of corners
						for l in range(4):
							for m in range(4):
								for n in range(4):
									triangle = np.array([boxes[i][l], boxes[j][m], boxes[k][n]])
									circumfrence = np.linalg.norm(triangle[0] - triangle[1]) + np.linalg.norm(triangle[1] - triangle[2]) + np.linalg.norm(triangle[2] - triangle[0])
									if circumfrence < min_circumfrence:
										min_circumfrence = circumfrence
										points = triangle

			#find center of triangle
			center = np.array([0.0, 0.0])
			for point in points:
				center += point
			center /= 3
			return points, center
		else:
			return None, None


		# return current_min_dists, current_min_dist_points



	def plot_bboxes(self, results, frame):
		
		xyxys = []
		confidences = []
		class_ids = []
		
		# Extract detections for blade class
		for result in results[0]:
			class_id = result.boxes.cls.cpu().numpy().astype(int)
			
			if class_id == 0 and result.boxes.conf.cpu().numpy()[0] > 0.5:
				
				xyxys.append(result.boxes.xyxy.cpu().numpy())
				confidences.append(result.boxes.conf.cpu().numpy())
				class_ids.append(result.boxes.cls.cpu().numpy().astype(int))
			
		
		# Setup detections for visualization
		detections = Detections(
					xyxy=results[0].boxes.xyxy.cpu().numpy(),
					confidence=results[0].boxes.conf.cpu().numpy(),
					class_id=results[0].boxes.cls.cpu().numpy().astype(int),
					)
		

		# Format custom labels
		self.labels = [f"{self.CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
		for _, confidence, class_id, tracker_id
		in detections if confidence > 0.4]
		
		# Annotate and display frame
		frame = self.box_annotator.annotate(frame=frame, detections=detections, labels=self.labels)
		
		return frame

	def detect(self):

		#test if gpu is available
		start_time = time()
		
		ret, frame = self.cap.read()
		assert ret
		
		results = self.predict(frame)
		frame = self.plot_bboxes(results, frame)
		points, center = self.get_turbine_center(results)
		# print(center)
		self.center = center
		if center is not None:
			cv2.circle(frame, (int(center[0]), int(center[1])), 10, (0, 255, 0), 2)
			dirString = '<--' if center[0] < 320 else '-->'
			cv2.putText(frame, dirString, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,0), 2)

		# print(points)
		if points is not None:
			for i in range(3):
				point1 = (int(points[i][0]), int(points[i][1]))
				point2 = (int(points[(i+1)%3][0]), int(points[(i+1)%3][1]))
				cv2.line(frame, point1, point2, (0, 255, 0), 2)

		end_time = time()
		fps = 1/np.round(end_time - start_time, 2)
			
		cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
		
		cv2.imshow('YOLOv8 Detection', frame)
		return self.center
	
	def close(self):
		self.cap.release()
		cv2.destroyAllWindows()


	def __call__(self):

		cap = cv2.VideoCapture(self.capture_index)
		assert cap.isOpened()
		cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		#test if gpu is available
		
		while True:
			
			start_time = time()
			
			ret, frame = cap.read()
			#print width and height of frame
			print(frame.shape)

			assert ret
			
			results = self.predict(frame)
			frame = self.plot_bboxes(results, frame)
			points, center = self.get_turbine_center(results)
			# print(center)
			self.center = center
			if center is not None:
				cv2.circle(frame, (int(center[0]), int(center[1])), 10, (0, 255, 0), 2)

			# print(points)
			if points is not None:
				for i in range(3):
					point1 = (int(points[i][0]), int(points[i][1]))
					point2 = (int(points[(i+1)%3][0]), int(points[(i+1)%3][1]))
					cv2.line(frame, point1, point2, (0, 255, 0), 2)

			# min_dists, min_dist_points = self.get_turbine_center(results)
			# print(min_dist_points[0][0])

			# for i in range(len(min_dists)):
			# 	point1 = (int(min_dist_points[i][0][0]), int(min_dist_points[i][0][1]))
			# 	point2 = (int(min_dist_points[i][1][0]), int(min_dist_points[i][1][1]))
			# 	cv2.line(frame, point1, point2, (0, 255, 0), 2)
			end_time = time()
			fps = 1/np.round(end_time - start_time, 2)
				
			cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
			
			cv2.imshow('YOLOv8 Detection', frame)
			# cv2.waitKey(0)

			if cv2.waitKey(5) & 0xFF == 27:
				
				break
		
		cap.release()
		cv2.destroyAllWindows()