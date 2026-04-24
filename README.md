# 🚗 SafeDriveAI – Real-Time Driver Monitoring System

SafeDriveAI is an **offline AI-based driver monitoring system** built using OpenCV and dlib.
It detects driver fatigue, distraction, and risky behavior in real time using a webcam.

---

## 🔥 Features

* 👁️ Eye Closure Detection (Drowsiness)
* 😮 Yawning Detection
* 🧠 Head Movement (Nod Detection)
* 👀 Distraction Detection (Face deviation)
* 💥 Crash Detection (motion + face disappearance)
* ⚠️ Risk Scoring System
* 🔊 Alert System (sound + visual warnings)
* 🚨 Emergency Recording System
* 💾 Circular Video Buffer

---

## 🛠️ Tech Stack

* Python
* OpenCV (cv2)
* dlib (facial landmarks)
* NumPy

---

## 📦 Setup Instructions

### 1. Install dependencies

```bash
pip install opencv-python dlib numpy scipy
```

---

### 2. Download model file

Download:
http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

Extract and place:

```
shape_predictor_68_face_landmarks.dat
```

inside the project folder.

---

### 3. Run the project

```bash
python main.py
```

---

## 🎮 Controls

* `t` → Toggle system ON/OFF
* `c` → Cancel emergency
* `q` → Quit

---

## ⚠️ Note

* Works completely offline
* No external APIs used
* Optimized for CPU (no GPU required)

---

## 🚀 Future Improvements

* Front camera road detection (AI)
* GPS + map-based hazard alerts
* Mobile integration
* Better UI dashboard

---

## 👨‍💻 Author

Manas Geedkar
