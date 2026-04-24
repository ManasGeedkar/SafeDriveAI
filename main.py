import cv2
import time

from utils import resize_frame
from facial_features import get_both_eyes_ear, calculate_mar, detect_distraction, get_nose_y
from state_manager import StateManager
from alert_system import AlertSystem
from video_buffer import VideoBuffer
from face_detection import FaceDetector
from glare import GlareDetector
from emergency import EmergencySystem
from crash_detection import CrashDetector

def main():
    try:
        face_detector = FaceDetector()
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print("[INFO] Starting video stream...")
    cap = cv2.VideoCapture(0)
    time.sleep(2.0)
    
    if not cap.isOpened():
        print("[ERROR] Camera failed to initialize.")
        return

    # Initialize Modules
    state_mgr = StateManager()
    alert_sys = AlertSystem(cooldown=5.0)
    video_buf = VideoBuffer(maxlen=600)
    glare_detector = GlareDetector()
    crash_detector = CrashDetector(motion_thresh=0.40)
    emergency_sys = EmergencySystem()

    system_active = True

    print("[INFO] SafeDriveAI is running.")
    print("Commands: 't' to toggle ON/OFF, 'c' to cancel emergency, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame. Exiting...")
            break
            
        frame = resize_frame(frame, width=360)
        video_buf.add_frame(frame)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        display_frame = frame.copy()
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('t'):
            system_active = not system_active
            if not system_active:
                state_mgr.reset()
            print(f"[INFO] System Active: {system_active}")
        elif key == ord('c'):
            if emergency_sys.active:
                emergency_sys.cancel()
                print("EMERGENCY CANCELLED")

        if not system_active:
            cv2.putText(display_frame, "SYSTEM OFF", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            cv2.imshow("SafeDriveAI", display_frame)
            continue

        # Feature extraction
        face_found, bbox, landmarks, is_fallback = face_detector.detect(gray)
        
        is_glare = glare_detector.detect(gray)
        is_crash = crash_detector.detect(gray, face_found)
        
        if is_crash and not emergency_sys.active:
            emergency_sys.trigger()
            print("[WARNING] Crash detected! Commencing countdown.")

        # Update Emergency State
        if emergency_sys.active:
            should_save, time_left = emergency_sys.update()
            if time_left > 0:
                cv2.putText(display_frame, f"EMERGENCY: {time_left}s", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            else:
                cv2.putText(display_frame, "EMERGENCY ENGAGED", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                if should_save:
                    print("[INFO] Saving crash video buffer...")
                    video_buf.save_buffer_async("crash_event.avi")

        if is_glare:
            cv2.putText(display_frame, "GLARE DETECTED", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        ear = mar = dest_ratio = nose_y = nose_shift_ratio = None
        
        if not face_found:
            cv2.putText(display_frame, "FACE NOT FOUND", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            (x, y, w, h) = bbox
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            try:
                # Calculate features
                if not is_fallback:
                    ear = get_both_eyes_ear(landmarks)
                    mar = calculate_mar(landmarks)
                
                dest_ratio = detect_distraction(landmarks)
                nose_y = get_nose_y(landmarks)
                
                # Calculate horizontal nose shift ratio for distraction
                nose_x = landmarks[30][0]
                box_center_x = x + w / 2.0
                nose_shift_ratio = abs(nose_x - box_center_x) / float(w)
                
                # Draw landmarks
                if not is_fallback:
                    for (lx, ly) in landmarks:
                        cv2.circle(display_frame, (lx, ly), 1, (255, 255, 255), -1)
            except Exception as e:
                # Handle feature fallback automatically by passing None
                pass

        # State and Temporal Logic Processing
        triggers, risk_score = state_mgr.update_state(ear, mar, dest_ratio, nose_y, nose_shift_ratio, is_glare)

        # UI & HUD rendering - Cleaned hierarchy to avoid overlap
        cv2.putText(display_frame, f"Risk Score: {state_mgr.total_risk_score:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        y_offset = 140
        for trigger in triggers:
            cv2.putText(display_frame, f"TRG: {trigger}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            y_offset += 25
            
        if risk_score >= state_mgr.alert_threshold:
            alert_sys.draw_alert(display_frame, "HIGH RISK")
            alert_sys.play_sound()

        cv2.imshow("SafeDriveAI", display_frame)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
