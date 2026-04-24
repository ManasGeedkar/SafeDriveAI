import numpy as np

class GlareDetector:
    def __init__(self, spike_threshold=50.0):
        self.prev_brightness = 100.0
        self.spike_threshold = spike_threshold
        
    def detect(self, gray_frame):
        current_brightness = np.mean(gray_frame)
        is_glare = False
        
        if current_brightness > self.prev_brightness + self.spike_threshold:
            is_glare = True
            
        self.prev_brightness = current_brightness
        return is_glare
