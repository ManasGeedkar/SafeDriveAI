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
        self.score_decay_rate = 0.005 # Gradual decay rate
        self.alert_threshold = 4.0

        # Glare logic
        self.glare_active = False
        self.glare_frames = 0
        self.glare_consec_frames = 0
        self.GLARE_SUPPRESSION_FRAMES = 40 # ~2 sec at 20fps
        
    def reset(self):
        self.total_risk_score = 0.0
        self.drowsy_frames = 0
        self.yawn_frames = 0
        self.distraction_frames = 0
        self.nod_frames = 0
        self.last_nose_y = None

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
                    self.total_risk_score += 0.15 # Gradual increase
                    alert_triggers.append("DROWSY")
            else:
                # Recovery logic: decrease frames gradually
                self.drowsy_frames = max(0, self.drowsy_frames - 1)

        # MAR processing (Yawning)
        if mar is not None:
            if mar > self.MAR_THRESH:
                self.yawn_frames += 1
                if self.yawn_frames >= self.YAWN_CONSEC_FRAMES:
                    self.total_risk_score += 0.1
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
                self.total_risk_score += 0.15
                alert_triggers.append("DISTRACTED")
        else:
            self.distraction_frames = max(0, self.distraction_frames - 1)

        # Nod logic
        if nose_y is not None:
            if self.last_nose_y is not None:
                velocity = abs(nose_y - self.last_nose_y)
                if velocity > self.nod_velocity_thresh:
                    self.nod_frames += 1
                    if self.nod_frames >= self.NOD_CONSEC_FRAMES:
                        self.total_risk_score += 1.0 # Instant but smaller jump
                        alert_triggers.append("HEAD NOD")
                else:
                    self.nod_frames = max(0, self.nod_frames - 1)
            self.last_nose_y = nose_y

        # Score Decay over time
        self.total_risk_score -= self.score_decay_rate
        if self.total_risk_score < 0:
            self.total_risk_score = 0.0
            
        return alert_triggers, self.total_risk_score
