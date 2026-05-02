# class StateManager:
#     def __init__(self):
#         # Frame counters
#         self.drowsy_frames = 0
#         self.yawn_frames = 0
#         self.distraction_frames = 0
#         self.nod_frames = 0
        
#         # Risk factors (Threshold parameters)
#         self.EAR_THRESH = 0.22 
#         self.DROWSY_CONSEC_FRAMES = 15
        
#         self.MAR_THRESH = 0.5
#         self.YAWN_CONSEC_FRAMES = 10
        
#         self.DISTRACTION_RATIO_THRESH_LOW = 0.6
#         self.DISTRACTION_RATIO_THRESH_HIGH = 1.6
#         self.DISTRACTION_CONSEC_FRAMES = 10
        
#         self.last_nose_y = None
#         self.nod_velocity_thresh = 5  # pixels per frame. Scaled depending on resolution
#         self.NOD_CONSEC_FRAMES = 5
        
#         # Scoring
#         self.total_risk_score = 0.0
#         self.score_decay_rate = 0.005 # Gradual decay rate
#         self.alert_threshold = 4.0

#         # Glare logic
#         self.glare_active = False
#         self.glare_frames = 0
#         self.glare_consec_frames = 0
#         self.GLARE_SUPPRESSION_FRAMES = 40 # ~2 sec at 20fps
        
#     def reset(self):
#         self.total_risk_score = 0.0
#         self.drowsy_frames = 0
#         self.yawn_frames = 0
#         self.distraction_frames = 0
#         self.nod_frames = 0
#         self.last_nose_y = None

#     def update_state(self, ear, mar, distraction_ratio, nose_y, nose_shift_ratio, is_glare):
#         alert_triggers = []
        
#         # Glare logic
#         if is_glare:
#             self.glare_consec_frames += 1
#             if self.glare_consec_frames >= 3:
#                 self.glare_active = True
#                 self.glare_frames = self.GLARE_SUPPRESSION_FRAMES
#         else:
#             self.glare_consec_frames = 0
            
#         if self.glare_frames > 0:
#             self.glare_frames -= 1
#             if self.glare_frames == 0:
#                 self.glare_active = False

#         if self.glare_active:
#             self.drowsy_frames = 0
#             self.yawn_frames = 0
#             self.distraction_frames = 0
#             self.nod_frames = 0
#             return [], self.total_risk_score

#         # EAR processing (Drowsiness)
#         if ear is not None:
#             if ear < self.EAR_THRESH:
#                 self.drowsy_frames += 1
#                 if self.drowsy_frames >= self.DROWSY_CONSEC_FRAMES:
#                     self.total_risk_score += 0.15 # Gradual increase
#                     alert_triggers.append("DROWSY")
#             else:
#                 # Recovery logic: decrease frames gradually
#                 self.drowsy_frames = max(0, self.drowsy_frames - 1)

#         # MAR processing (Yawning)
#         if mar is not None:
#             if mar > self.MAR_THRESH:
#                 self.yawn_frames += 1
#                 if self.yawn_frames >= self.YAWN_CONSEC_FRAMES:
#                     self.total_risk_score += 0.1
#                     alert_triggers.append("YAWNING")
#             else:
#                 self.yawn_frames = max(0, self.yawn_frames - 1)

#         # Distraction processing
#         distracted = False
#         if distraction_ratio is not None and (distraction_ratio < self.DISTRACTION_RATIO_THRESH_LOW or distraction_ratio > self.DISTRACTION_RATIO_THRESH_HIGH):
#             distracted = True
#         elif nose_shift_ratio is not None and nose_shift_ratio > 0.25:
#             distracted = True
            
#         if distracted:
#             self.distraction_frames += 1
#             if self.distraction_frames >= self.DISTRACTION_CONSEC_FRAMES:
#                 self.total_risk_score += 0.15
#                 alert_triggers.append("DISTRACTED")
#         else:
#             self.distraction_frames = max(0, self.distraction_frames - 1)

#         # Nod logic
#         if nose_y is not None:
#             if self.last_nose_y is not None:
#                 velocity = abs(nose_y - self.last_nose_y)
#                 if velocity > self.nod_velocity_thresh:
#                     self.nod_frames += 1
#                     if self.nod_frames >= self.NOD_CONSEC_FRAMES:
#                         self.total_risk_score += 1.0 # Instant but smaller jump
#                         alert_triggers.append("HEAD NOD")
#                 else:
#                     self.nod_frames = max(0, self.nod_frames - 1)
#             self.last_nose_y = nose_y

#         # Score Decay over time
#         self.total_risk_score -= self.score_decay_rate
#         if self.total_risk_score < 0:
#             self.total_risk_score = 0.0
            
#         return alert_triggers, self.total_risk_score

class StateManager:
    def __init__(self):
        # Frame counters
        self.drowsy_frames = 0
        self.yawn_frames = 0
        self.distraction_frames = 0
        self.nod_frames = 0
        
        # Risk factors (Threshold parameters)
        self.EAR_THRESH = 0.22 
        self.DROWSY_CONSEC_FRAMES = 15
        
        self.MAR_THRESH = 0.5
        self.YAWN_CONSEC_FRAMES = 10
        
        self.DISTRACTION_RATIO_THRESH_LOW = 0.6
        self.DISTRACTION_RATIO_THRESH_HIGH = 1.6
        self.DISTRACTION_CONSEC_FRAMES = 10
        
        self.last_nose_y = None
        self.nod_velocity_thresh = 5  # pixels per frame. Scaled depending on resolution
        self.NOD_CONSEC_FRAMES = 5
        
        # Scoring
        self.total_risk_score = 0.0
        self.score_decay_rate = 0.015 # Slightly slower decay to allow risk to build
        self.alert_threshold = 3.0   # Lowered threshold for faster alerts

        # Glare logic
        self.glare_active = False
        self.glare_frames = 0
        self.glare_consec_frames = 0
        self.GLARE_SUPPRESSION_FRAMES = 40 # ~2 sec at 20fps
        
        # ✅ NEW: Confirmation logic for 5-second delay
        self.alert_timer = 0
        self.ALERT_DELAY_FRAMES = 100 # ~5 seconds at 20fps
        
    def reset(self):
        self.total_risk_score = 0.0
        self.drowsy_frames = 0
        self.yawn_frames = 0
        self.distraction_frames = 0
        self.nod_frames = 0
        self.last_nose_y = None
        self.alert_timer = 0 # Reset timer

    def update_state(self, ear, mar, distraction_ratio, nose_y, nose_shift_ratio, is_glare):
        alert_triggers = []
        
        # Glare logic
        if is_glare:
            self.glare_consec_frames += 1
            if self.glare_consec_frames >= 3:
                self.glare_active = True
                self.glare_frames = self.GLARE_SUPPRESSION_FRAMES
        else:
            self.glare_consec_frames = 0
            
        if self.glare_frames > 0:
            self.glare_frames -= 1
            if self.glare_frames == 0:
                self.glare_active = False

        if self.glare_active:
            self.drowsy_frames = 0
            self.yawn_frames = 0
            self.distraction_frames = 0
            self.nod_frames = 0
            return [], self.total_risk_score

        # EAR processing (Drowsiness)
        if ear is not None:
            if ear < self.EAR_THRESH:
                self.drowsy_frames += 1
                if self.drowsy_frames >= self.DROWSY_CONSEC_FRAMES:
                    self.total_risk_score += 0.2 # Accumulate every frame
                    alert_triggers.append("DROWSY")
            else:
                # Recovery logic: decrease frames gradually
                self.drowsy_frames = max(0, self.drowsy_frames - 1)

        # MAR processing (Yawning)
        if mar is not None:
            if mar > self.MAR_THRESH:
                self.yawn_frames += 1
                if self.yawn_frames >= self.YAWN_CONSEC_FRAMES:
                    self.total_risk_score += 0.15
                    alert_triggers.append("YAWNING")
            else:
                self.yawn_frames = max(0, self.yawn_frames - 1)

        # Distraction processing
        distracted = False
        if distraction_ratio is not None and (distraction_ratio < self.DISTRACTION_RATIO_THRESH_LOW or distraction_ratio > self.DISTRACTION_RATIO_THRESH_HIGH):
            distracted = True
        elif nose_shift_ratio is not None and nose_shift_ratio > 0.25:
            distracted = True
            
        if distracted:
            self.distraction_frames += 1
            if self.distraction_frames >= self.DISTRACTION_CONSEC_FRAMES:
                self.total_risk_score += 0.2
                alert_triggers.append("DISTRACTED")
        else:
            self.distraction_frames = max(0, self.distraction_frames - 3)

        # Nod logic
        if nose_y is not None:
            if self.last_nose_y is not None:
                velocity = abs(nose_y - self.last_nose_y)
                if velocity > self.nod_velocity_thresh:
                    self.nod_frames += 1
                    if self.nod_frames >= self.NOD_CONSEC_FRAMES:
                        self.total_risk_score += 1.2 # Slightly lower to avoid instant max
                        alert_triggers.append("HEAD NOD")
                        self.nod_frames = 0 # Reset to prevent spamming
                else:
                    self.nod_frames = max(0, self.nod_frames - 1)
            self.last_nose_y = nose_y

        # ✅ Dynamic Score Decay over time
        # If no active triggers, decay much faster (Fast Reset)
        if not alert_triggers:
            self.total_risk_score -= self.score_decay_rate * 4
        else:
            self.total_risk_score -= self.score_decay_rate

        # ✅ Risk Capping (Prevents score from getting too "stuck" high)
        if self.total_risk_score < 0:
            self.total_risk_score = 0.0
        self.total_risk_score = min(self.total_risk_score, 5.0)

        # ✅ NEW: 5-Second Confirmation Timer
        if self.total_risk_score >= self.alert_threshold:
            self.alert_timer += 1
        else:
            self.alert_timer = 0
        
        is_confirmed = (self.alert_timer >= self.ALERT_DELAY_FRAMES)
            
        return alert_triggers, self.total_risk_score, is_confirmed

