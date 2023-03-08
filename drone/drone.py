import cv2 as cv2
import numpy as np

# Create a VideoCapture object for the webcam
cap = cv2.VideoCapture(1)

while True:
    # Capture frame-by-frame
	ret, frame = cap.read()

	blur = cv2.GaussianBlur(frame, (7, 7), 2)
	h, w = frame.shape[:2]

	# Morphological gradient

	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
	gradient = cv2.morphologyEx(blur, cv2.MORPH_GRADIENT, kernel)
	# cv2.imshow('Morphological gradient', gradient)

	# Binarize gradient

	lowerb = np.array([0, 0, 0])
	upperb = np.array([15, 15, 15])
	binary = cv2.inRange(gradient, lowerb, upperb)
	cv2.imshow('Binarized gradient', binary)

	# Flood fill from the edges to remove edge crystals

	for row in range(h):
		if binary[row, 0] == 255:
			cv2.floodFill(binary, None, (0, row), 0)
		if binary[row, w-1] == 255:
			cv2.floodFill(binary, None, (w-1, row), 0)

	for col in range(w):
		if binary[0, col] == 255:
			cv2.floodFill(binary, None, (col, 0), 0)
		if binary[h-1, col] == 255:
			cv2.floodFill(binary, None, (col, h-1), 0)
	cv2.imshow('Filled binary gradient', binary)

	foreground = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
	foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)
	cv2.imshow('Cleanup up crystal foreground mask', foreground)


    # Wait for 'q' key to exit
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()


