import cv2
import threading
from collections import deque
import time
import os

class VideoBuffer:
    def __init__(self, maxlen=600): # ~30 seconds at 20fps
        self.buffer = deque(maxlen=maxlen)
        self.saving = False

    def add_frame(self, frame):
        self.buffer.append(frame.copy())

    def save_buffer_async(self, filename="crash_log.avi", fps=20.0):
        if self.saving or len(self.buffer) == 0:
            return
        
        self.saving = True
        # Extract frames so that the buffer we save isn't modified during write
        frames_to_save = list(self.buffer)
        
        thread = threading.Thread(target=self._save_video, args=(frames_to_save, filename, fps))
        thread.start()
        
    def _save_video(self, frames, filename, fps):
        try:
            height, width = frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            full_filename = f"{timestamp}_{filename}"
            
            out = cv2.VideoWriter(full_filename, fourcc, fps, (width, height))
            for frame in frames:
                out.write(frame)
            out.release()
        finally:
            self.saving = False
