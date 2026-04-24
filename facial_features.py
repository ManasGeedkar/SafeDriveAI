from utils import euclidean_distance

def calculate_ear(eye):
    A = euclidean_distance(eye[1], eye[5])
    B = euclidean_distance(eye[2], eye[4])
    C = euclidean_distance(eye[0], eye[3])
    if C == 0:
        return 0.0
    return (A + B) / (2.0 * C)

def get_both_eyes_ear(landmarks):
    leftEye = landmarks[36:42]
    rightEye = landmarks[42:48]
    leftEAR = calculate_ear(leftEye)
    rightEAR = calculate_ear(rightEye)
    return (leftEAR + rightEAR) / 2.0

def calculate_mar(landmarks):
    mouth = landmarks[48:68]
    # Inner mouth points: 61,62,63, 65,66,67
    # Mapped to mouth indices starting from 0 -> 48
    # 61->13, 62->14, 63->15, 65->17, 66->18, 67->19
    # 48->0, 54->6
    A = euclidean_distance(mouth[13], mouth[19])
    B = euclidean_distance(mouth[14], mouth[18])
    C = euclidean_distance(mouth[15], mouth[17])
    D = euclidean_distance(mouth[0], mouth[6])
    if D == 0:
        return 0.0
    return (A + B + C) / (3.0 * D)

def detect_distraction(landmarks):
    nose_tip = landmarks[30]
    left_side = landmarks[0]  # Left edge of face
    right_side = landmarks[16] # Right edge of face
    
    dist_left = euclidean_distance(nose_tip, left_side)
    dist_right = euclidean_distance(nose_tip, right_side)
    
    if dist_right == 0:
        return 1.0
    return dist_left / dist_right

def get_nose_y(landmarks):
    return landmarks[30][1]
