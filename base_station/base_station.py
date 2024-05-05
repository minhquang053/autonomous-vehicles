import numpy as np
from video_proc import VideoProcessor
from utils import tcp_client

class BaseStation:
	def __init__(self, mode='detect'):
		self.connected = False
		self.mode = mode
	
	def connect(self, host, port=65432, in_msg_label='', out_msg_label=''):
		self.send_command, self.close_connection = tcp_client(host, port, in_msg_label, out_msg_label)
		self.vproc = VideoProcessor(host)
		self.connected = True
	
	def get_decision(bbox, width=640):
		x, w = int(bbox[0]), int(bbox[2])
		cx = int(x + w // 2)

		# Calculate slope
		if cx < width // 2 - 50: 
			return "Tracking: Left"
		elif cx > width // 2 + 50: 
			return "Tracking: Right"
		else:  
			return "Tracking: Forward"
	
	def real_time_control(self):
		if self.connected:
			frame = self.vproc.get_latest_frame()

			if self.mode == 'tracking':	
				ok, bbox = self.vproc.tracking(frame)
				if ok:
					self.send_command(self.get_decision(bbox, frame.shape[1]))
				else :
					self.mode = 'detect'
			elif self.mode == 'detect': 
				detected, bbox = self.vproc.detect(frame, 'bottle')
				if detected:	
					self.vproc.tracker = self.vproc.init_tracker(frame, bbox)
					self.mode = 'tracking'
				else:
					self.send_command('Detecting')
			elif self.mode == 'manual':
				pass

			return True, frame
		else:
			return False, None 

	def close(self):
		self.vproc.close()
		self.close_connection()