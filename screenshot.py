import cv2
import mediapipe as mp
import pyautogui
import time
import math
import os
import subprocess
import numpy as np

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def get_eye_ratio(landmarks, eye_indices, frame_width, frame_height):
    points = []
    for idx in eye_indices:
        x = int(landmarks[idx].x * frame_width)
        y = int(landmarks[idx].y * frame_height)
        points.append((x, y))

    left_right = math.dist(points[0], points[3])
    top_bottom = (math.dist(points[1], points[5]) + math.dist(points[2], points[4])) / 2.0
    return top_bottom / left_right

def count_fingers(hand_landmarks):
    tips_ids = [8, 12, 16, 20]
    count = 0
    for tip_id in tips_ids[:3]:  # Only check first 3 fingers (index, middle, ring)
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            count += 1
    return count

def show_notification(title, message):
    subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])

def speak_message(message):
    subprocess.run(['say', '-v', 'Samantha', message])

def play_sound():
    subprocess.run(['afplay', '/System/Library/Sounds/Submarine.aiff'])

# Start screen recording using ffmpeg
def start_screen_recording(filename):
    return subprocess.Popen([
        'ffmpeg', '-y',
        '-f', 'avfoundation', '-framerate', '30', '-i', '1:none',
        '-pix_fmt', 'yuv420p', filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Stop screen recording
def stop_screen_recording(process):
    process.terminate()

cap = cv2.VideoCapture(0)

blink_counter = 0
last_blink_time = 0
blink_times = []

recording_process = None
recording = False
last_gesture_time = 0

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Face processing
    face_results = face_mesh.process(rgb)

    # Hand processing
    hand_results = hands.process(rgb)

    # --- Blink detection ---
    if face_results.multi_face_landmarks:
        mesh = face_results.multi_face_landmarks[0]

        left_eye_ratio = get_eye_ratio(mesh.landmark, LEFT_EYE, frame_width, frame_height)
        right_eye_ratio = get_eye_ratio(mesh.landmark, RIGHT_EYE, frame_width, frame_height)

        blink_threshold = 0.22

        if left_eye_ratio < blink_threshold and right_eye_ratio < blink_threshold:
            current_time = time.time()
            if current_time - last_blink_time > 0.1:
                blink_times.append(current_time)
                last_blink_time = current_time
                print(f"Blink detected!")

            blink_times = [t for t in blink_times if current_time - t <= 2]

            if len(blink_times) == 2:
                if blink_times[-1] - blink_times[-2] <= 1:
                    print("Double blink! Taking screenshot...")
                    filename = os.path.join(desktop_path, f"screenshot_{int(time.time())}.png")
                    screenshot = pyautogui.screenshot()
                    screenshot.save(filename)

                    show_notification("Screenshot Taken", f"Saved as {os.path.basename(filename)}")
                    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    preview = cv2.resize(screenshot_cv, (400, 300))
                    cv2.imshow("Preview", preview)
                    cv2.waitKey(1500)
                    cv2.destroyWindow("Preview")

                    play_sound()
                    speak_message("Screenshot captured!")
                    time.sleep(2)
                    blink_times = []

    # --- Hand gesture for 3 fingers ---
    if hand_results.multi_hand_landmarks:
        current_time = time.time()
        if current_time - last_gesture_time > 2:  # prevent spamming
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            finger_count = count_fingers(hand_landmarks)

            if finger_count == 3:
                if not recording:
                    filename = os.path.join(desktop_path, f"screen_record_{int(time.time())}.mp4")
                    recording_process = start_screen_recording(filename)
                    recording = True
                    show_notification("Screen Recording", "Recording started!")
                    speak_message("Recording started")
                    print("Started recording...")
                else:
                    stop_screen_recording(recording_process)
                    recording = False
                    show_notification("Screen Recording", "Recording stopped and saved.")
                    speak_message("Recording stopped")
                    print("Stopped recording...")

                last_gesture_time = current_time

    cv2.imshow("Blink + Gesture Control App", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
