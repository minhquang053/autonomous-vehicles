import numpy as np
from video_proc import VideoProcessor
from utils import tcp_client
import traceback
from dataclasses import dataclass

@dataclass
class SystemInfo:
	sent_msg: str
	recv_msg: str
	vehicle_type: str

class BaseStation:
	def __init__(self, mode='detect'):
		self.connected = False
		self.mode = mode
		self.sys_info = SystemInfo('', '', '')
	
	def connect(self, host, port=65432):
		self.send_command, self.close_connection = tcp_client(host, port, self.sys_info)
		self.vproc = VideoProcessor(host)
		self.connected = True
	
	def get_decision(self, bbox, width=640):
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
			try:
				frame = self.vproc.get_latest_frame()

				if self.mode == 'tracking':	
					ok, bbox = self.vproc.tracking(frame)
					if ok:
						self.send_command(self.get_decision(bbox))
					else :
						self.mode = 'detect'
				elif self.mode == 'detect': 
					detected, bbox = self.vproc.detect(frame, 'person')
					if detected:	
						self.vproc.tracker = self.vproc.init_tracker(frame, bbox, 'person')
						self.mode = 'tracking'
					else:
						self.send_command('Detecting')
				elif self.mode == 'manual':
					pass
			except Exception:
				traceback.print_exc()

			return True, frame
		else:
			return False, None 

	def close(self):
		self.vproc.close()
		self.close_connection()
