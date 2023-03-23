import serial
import time

class Drone:
	ser = None

	def __init__(self):
		self.ser = serial.Serial(port='COM5', baudrate=9600, timeout=1)  # open first serial port
		print("port name: " + self.ser.name)         # check which port was really used
		time.sleep(1.6)
		print("serial initialized")

	def writeToSerial(self, data):
		self.ser.write(bytes(data, 'utf-8'))
	
	def readFromSerial(self):
		return self.ser.readline().decode('utf-8')
	
	def moveAbs(self,x,y):
		self.writeToSerial("abs" + str(x) + "," + str(y))

	def moveRel(self,x,y):
		self.writeToSerial("rel" + str(x) + "," + str(y))

	def moveDir(self, axis, direction, speed):
		dirString = "-" if direction == -1 else "+"
		self.writeToSerial("mve" + dirString + axis + "," + str(speed))
		while True:
			read = self.readFromSerial().strip()
			if read == "moving":
				break

	def stop(self, axis):
		self.writeToSerial("stp" + axis)
		while True:
			read = self.readFromSerial().strip()
			if read == "stopped":
				break
	
	def home(self):
		self.writeToSerial('home')
		while True:
			read = self.readFromSerial().strip()
			if read == "homing done":
				break
	
	# def waitForSerial(self):
	# 	self.ser.

	def getPosition(self):
		self.writeToSerial("position")
		time.sleep(0.001)
		return self.readFromSerial()
