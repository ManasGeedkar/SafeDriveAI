# import winsound
# import time
# import cv2

# class AlertSystem:
#     def __init__(self, cooldown=5.0):
#         self.cooldown = cooldown
#         self.last_alert_time = 0.0

#     def play_sound(self):
#         current_time = time.time()
#         if (current_time - self.last_alert_time) >= self.cooldown:
#             print("ALERT TRIGGERED")
#             try:
#                 # Use Beep for guaranteed audible feedback on Windows
#                 winsound.Beep(1000, 300)
#                 print("SOUND PLAYED")
#             except Exception as e:
#                 # Fallback to system sound if Beep fails
#                 winsound.MessageBeep()
#                 print("SOUND PLAYED (Fallback)")
#             self.last_alert_time = current_time
#             return True
#         return False
        
#     def draw_alert(self, frame, text):
#         # Shifted downwards to avoid overlapping with Risk Score
#         cv2.putText(frame, "WARNING: " + text, (10, 90),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
import winsound
import time
import cv2

class AlertSystem:
    def __init__(self, cooldown=0.4): # Faster repeat for continuous sound
        self.cooldown = cooldown
        self.last_alert_time = 0.0

    def play_sound(self):
        current_time = time.time()

        # ❌ Repeat Interval check
        if (current_time - self.last_alert_time) < self.cooldown:
            return False

        self.last_alert_time = current_time

        print("ALERT TRIGGERED")

        try:
            winsound.Beep(1000, 200) # Slightly shorter beep for continuous feel
            print("SOUND PLAYED")
        except:
            winsound.MessageBeep()
            print("SOUND PLAYED (Fallback)")

        return True

    def reset_alert(self):
        # ✅ Call this when condition becomes NORMAL
        self.alert_active = False

    def draw_alert(self, frame, text):
        cv2.putText(frame, "WARNING: " + text, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

