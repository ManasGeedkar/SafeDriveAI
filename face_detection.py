# import dlib
# import os
# import cv2
# from utils import rect_to_bb, shape_to_np

# class FaceDetector:
#     def __init__(self, predictor_path="shape_predictor_68_face_landmarks.dat"):
#         if not os.path.exists(predictor_path):
#             raise FileNotFoundError(f"{predictor_path} not found. Please ensure it's in the directory.")
        
#         self.detector = dlib.get_frontal_face_detector()
#         self.predictor = dlib.shape_predictor(predictor_path)
        
#         self.frame_count = 0
#         self.detect_interval = 4  # Full detection every 4 frames
#         self.last_rect = None
#         self.face_missing_frames = 0
#         self.MISSING_THRESH = 15

#     def detect(self, gray_frame):
#         # Robustness improvement
#         gray_frame = cv2.equalizeHist(gray_frame)
#         self.frame_count += 1
        
#         need_detect = (self.frame_count % self.detect_interval == 0) or (self.last_rect is None)
        
#         if need_detect:
#             rects = self.detector(gray_frame, 0)
#             if len(rects) > 0:
#                 self.last_rect = rects[0]
#                 self.face_missing_frames = 0
#             else:
#                 if self.last_rect is not None:
#                     self.face_missing_frames += 1
#                 else:
#                     self.face_missing_frames += 1
#         else:
#             # We are not doing a full detection, but we increment missing frames if we don't have a confirmed face
#             if self.face_missing_frames > 0:
#                 self.face_missing_frames += 1
                
#         if self.last_rect is None:
#             return False, None, None, False
            
#         if self.face_missing_frames > self.MISSING_THRESH:
#             self.last_rect = None
#             self.face_missing_frames = 0
#             return False, None, None, False

#         bbox = rect_to_bb(self.last_rect)
#         shape = self.predictor(gray_frame, self.last_rect)
#         landmarks = shape_to_np(shape)
        
#         is_fallback = (self.face_missing_frames > 0)
        
#         return True, bbox, landmarks, is_fallback


import dlib
import os
import cv2
from utils import rect_to_bb, shape_to_np

class FaceDetector:
    def __init__(self, predictor_path="shape_predictor_68_face_landmarks.dat"):
        if not os.path.exists(predictor_path):
            raise FileNotFoundError(f"{predictor_path} not found. Please ensure it's in the directory.")
        
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
        
        self.frame_count = 0
        self.detect_interval = 2 # Full detection every 4 frames
        self.last_rect = None
        self.last_landmarks = None # ✅ NEW: For smoothing
        self.face_missing_frames = 0
        self.MISSING_THRESH = 30 # More lenient for head turns

    def detect(self, gray_frame):
        gray_frame = cv2.equalizeHist(gray_frame)
        # ❌ REMOVED: Resizing here makes it too hard to detect distant faces
        # gray_frame = cv2.resize(gray_frame, (0, 0), fx=0.5, fy=0.5)
        self.frame_count += 1
        
        need_detect = (self.frame_count % self.detect_interval == 0) or (self.last_rect is None)
        
        if need_detect:
            rects = self.detector(gray_frame, 1) # Upsample 1 time for better sensitivity
            if len(rects) > 0:
                target_rect = max(rects, key=lambda r: r.width() * r.height())
                if self.last_rect is None:
                    self.last_rect = target_rect
                else:
                    # ✅ Smoothly interpolate to avoid flickering
                    alpha = 0.6
                    self.last_rect = dlib.rectangle(
                        int(self.last_rect.left() * (1 - alpha) + target_rect.left() * alpha),
                        int(self.last_rect.top() * (1 - alpha) + target_rect.top() * alpha),
                        int(self.last_rect.right() * (1 - alpha) + target_rect.right() * alpha),
                        int(self.last_rect.bottom() * (1 - alpha) + target_rect.bottom() * alpha)
                    )
                self.face_missing_frames = 0
            else:
                if self.last_rect is not None:
                    self.face_missing_frames += 1
                else:
                    self.face_missing_frames += 1
        else:
            # We are not doing a full detection, but we increment missing frames if we don't have a confirmed face
            # if self.face_missing_frames > 0:
            #     self.face_missing_frames += 1
            # tracking mode → do NOT increase missing frames aggressively
                pass
            
        if self.last_rect is None:
            return False, None, None, False
            
        if self.face_missing_frames > self.MISSING_THRESH:
            self.last_rect = None
            self.face_missing_frames = 0
            return False, None, None, False

        bbox = rect_to_bb(self.last_rect)
        shape = self.predictor(gray_frame, self.last_rect)
        current_landmarks = shape_to_np(shape)
        
        # ✅ NEW: Smooth landmarks to eliminate jitter
        if self.last_landmarks is None:
            self.last_landmarks = current_landmarks
        else:
            alpha_l = 0.4 # Smoothing factor for landmarks
            self.last_landmarks = (self.last_landmarks * (1 - alpha_l) + current_landmarks * alpha_l).astype(int)

        # REMOVED: Updating last_rect from landmarks caused bounding box to collapse when turning face.
        # The detector runs every 2 frames, which is enough to track the face.
        
        is_fallback = (self.face_missing_frames > 0)
        
        return True, bbox, self.last_landmarks, is_fallback
