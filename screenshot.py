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

# Finger connections for drawing lines (from wrist to fingertips)
FINGER_CONNECTIONS = [
    (0, 1, 2, 3, 4),    # Thumb
    (0, 5, 6, 7, 8),    # Index
    (0, 9, 10, 11, 12),  # Middle
    (0, 13, 14, 15, 16), # Ring
    (0, 17, 18, 19, 20)  # Pinky
]

def get_eye_ratio(landmarks, eye_indices, frame_width, frame_height):
    points = []
    for idx in eye_indices:
        x = int(landmarks[idx].x * frame_width)
        y = int(landmarks[idx].y * frame_height)
        points.append((x, y))
    left_right = math.dist(points[0], points[3])
    top_bottom = (math.dist(points[1], points[5]) + math.dist(points[2], points[4])) / 2.0
    return top_bottom / left_right

def get_eye_bounding_box(landmarks, eye_indices, frame_width, frame_height):
    points = []
    for idx in eye_indices:
        x = int(landmarks[idx].x * frame_width)
        y = int(landmarks[idx].y * frame_height)
        points.append((x, y))
    
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    padding = 10
    return (x_min - padding, y_min - padding, x_max + padding, y_max + padding)

def count_fingers(hand_landmarks):
    finger_tips = [8, 12, 16]  # Index, Middle, Ring fingertips
    finger_knuckles = [6, 10, 14]  # Corresponding knuckles
    
    count = 0
    for tip_id, knuckle_id in zip(finger_tips, finger_knuckles):
        tip_y = hand_landmarks.landmark[tip_id].y
        knuckle_y = hand_landmarks.landmark[knuckle_id].y
        if tip_y < knuckle_y:  # Finger is up when tip is above knuckle
            count += 1
    return count

def draw_finger_lines(frame, hand_landmarks, frame_width, frame_height):
    for finger in FINGER_CONNECTIONS:
        for i in range(len(finger) - 1):
            start = finger[i]
            end = finger[i + 1]
            start_point = (int(hand_landmarks.landmark[start].x * frame_width),
                         int(hand_landmarks.landmark[start].y * frame_height))
            end_point = (int(hand_landmarks.landmark[end].x * frame_width),
                        int(hand_landmarks.landmark[end].y * frame_height))
            cv2.line(frame, start_point, end_point, (255, 0, 0), 2)

def get_hand_bounding_box(hand_landmarks, frame_width, frame_height):
    x_coords = [int(lm.x * frame_width) for lm in hand_landmarks.landmark]
    y_coords = [int(lm.y * frame_height) for lm in hand_landmarks.landmark]
    
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    padding = 20
    return (x_min - padding, y_min - padding, x_max + padding, y_max + padding)

def show_notification(title, message):
    subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])

def speak_message(message):
    subprocess.run(['say', '-v', 'Samantha', message])

def play_sound():
    subprocess.run(['afplay', '/System/Library/Sounds/Submarine.aiff'])

def start_screen_recording(filename):
    return subprocess.Popen([
        'ffmpeg', '-y',
        '-f', 'avfoundation', '-framerate', '30', '-i', '1:none',
        '-pix_fmt', 'yuv420p', filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_screen_recording(process):
    process.terminate()

cap = cv2.VideoCapture(0)

blink_counter = 0
last_blink_time = 0
blink_times = []

recording_process = None
recording = False
last_gesture_time = 0
three_finger_start_time = None

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

    # --- Blink detection and eye bounding boxes ---
    if face_results.multi_face_landmarks:
        mesh = face_results.multi_face_landmarks[0]

        left_eye_ratio = get_eye_ratio(mesh.landmark, LEFT_EYE, frame_width, frame_height)
        right_eye_ratio = get_eye_ratio(mesh.landmark, RIGHT_EYE, frame_width, frame_height)

        left_box = get_eye_bounding_box(mesh.landmark, LEFT_EYE, frame_width, frame_height)
        right_box = get_eye_bounding_box(mesh.landmark, RIGHT_EYE, frame_width, frame_height)
        
        cv2.rectangle(frame, (left_box[0], left_box[1]), (left_box[2], left_box[3]), (0, 255, 0), 2)
        cv2.rectangle(frame, (right_box[0], right_box[1]), (right_box[2], right_box[3]), (0, 255, 0), 2)

        blink_threshold = 0.12

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
                    preview = cv2.resize(screenshot_cv, (500, 400))
                    cv2.imshow("Preview", preview)
                    cv2.waitKey(1500)
                    cv2.destroyWindow("Preview")

                    play_sound()
                    speak_message("Screenshot captured!")
                    time.sleep(2)
                    blink_times = []

    # --- Hand gesture detection and bounding box ---
    if hand_results.multi_hand_landmarks:
        current_time = time.time()
        hand_landmarks = hand_results.multi_hand_landmarks[0]
        
        hand_box = get_hand_bounding_box(hand_landmarks, frame_width, frame_height)
        cv2.rectangle(frame, (hand_box[0], hand_box[1]), (hand_box[2], hand_box[3]), (0, 0, 255), 2)
        
        # Draw finger lines
        draw_finger_lines(frame, hand_landmarks, frame_width, frame_height)
        
        finger_count = count_fingers(hand_landmarks)
        
        # Display finger count with proper singular/plural form
        finger_text = "Finger" if finger_count == 1 else "Fingers"
        cv2.putText(frame, f'{finger_text}: {finger_count}', 
                   (hand_box[0], hand_box[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        if current_time - last_gesture_time > 2:  # prevent spamming
            if finger_count == 3:
                if three_finger_start_time is None:
                    three_finger_start_time = current_time
                    cv2.putText(frame, 'Hold for 1 sec...', 
                               (hand_box[0], hand_box[3] + 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                elif current_time - three_finger_start_time >= 1:
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
                    three_finger_start_time = None
            else:
                three_finger_start_time = None

    cv2.imshow("Blink + Gesture Control App", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
