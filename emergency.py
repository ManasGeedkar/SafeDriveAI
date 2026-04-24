import time

class EmergencySystem:
    def __init__(self):
        self.countdown_duration = 10
        self.start_time = 0
        self.active = False
        self.saving = False
        self.cooldown_end = 0

    def trigger(self):
        if not self.active and time.time() > self.cooldown_end:
            self.active = True
            self.start_time = time.time()
            self.saving = False
            
    def cancel(self):
        self.active = False
        self.saving = False
        self.cooldown_end = time.time() + 5.0

    def update(self):
        if not self.active:
            return False, 0
            
        time_elapsed = time.time() - self.start_time
        time_left = max(0, self.countdown_duration - int(time_elapsed))
        
        if time_left == 0 and not self.saving:
            self.saving = True
            return True, 0 # Returns tuple (should_save_video, time_left)
            
        return False, time_left
