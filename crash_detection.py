import cv2

class CrashDetector:
    def __init__(self, motion_thresh=0.40):
        self.prev_gray = None
        self.motion_thresh = motion_thresh
        self.face_missing_frames = 0
        self.crash_consec_frames = 0
        
    def detect(self, current_gray, face_found):
        if self.prev_gray is None:
            self.prev_gray = current_gray.copy()
            return False
            
        diff = cv2.absdiff(self.prev_gray, current_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        non_zero = cv2.countNonZero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        magnitude = non_zero / float(total_pixels)
        
        self.prev_gray = current_gray.copy()
        
        if not face_found:
            self.face_missing_frames += 1
        else:
            self.face_missing_frames = 0
            
        if magnitude > self.motion_thresh and self.face_missing_frames > 5:
            self.crash_consec_frames += 1
            if self.crash_consec_frames >= 3:
                return True
        else:
            self.crash_consec_frames = 0
            
        return False
