import mediapipe as mp
import cv2
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

counter = 0
state = None  # "up" or "down"

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def count_squat(landmarks, frame_width, frame_height):
    global counter, state

    # Extract coordinates
    hip = [landmarks[24].x * frame_width, landmarks[24].y * frame_height]
    knee = [landmarks[26].x * frame_width, landmarks[26].y * frame_height]
    ankle = [landmarks[28].x * frame_width, landmarks[28].y * frame_height]

    knee_angle = calculate_angle(hip, knee, ankle)

    # Rep counting logic
    if knee_angle > 160:
        if state == "down":
            counter += 1
            state = "up"
    elif knee_angle < 90:
        if state == "up" or state is None:
            state = "down"

    return counter, knee_angle

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        counter, angle = count_squat(results.pose_landmarks.landmark,
                                     frame.shape[1], frame.shape[0])

        # Display angle and rep count on frame
        cv2.putText(frame, f"Knee Angle: {int(angle)}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f"Reps: {counter}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow('MediaPipe Pose', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
