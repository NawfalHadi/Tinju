import os
import warnings
import time
import cv2
import pandas as pd
import numpy as np
import socket

import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import pickle

# from main.helper.constants import *

SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345

def send_data(value):
    sock.sendall(value.encode())

connected = False

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

model_path = "main/gameplay/model/boxing_form.pkl"

with open(model_path, 'rb') as f:
    model = pickle.load(f)

box_form = [False, False, False, False, False]

time.sleep(1)
cap = cv2.VideoCapture(0)

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False   

        results = holistic.process(image)

        if results.pose_landmarks:
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Get specific landmarks
            wrist_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_WRIST]
            elbow_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_ELBOW]
            wrist_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_WRIST]
            elbow_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_ELBOW]

            lm = landmark_pb2.NormalizedLandmarkList()
            lm.landmark.extend([wrist_l, wrist_r, elbow_l, elbow_r])

            for landmark in lm.landmark:
                x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
                cv2.circle(image, (x, y), 5, (255, 0, 0), -1)

            try:
                pose = lm.landmark
                pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())
                
                pose_detected = pd.DataFrame([pose_row])
                warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
                
                body_language_class = model.predict(pose_detected)[0]
                body_language_prob = model.predict_proba(pose_detected)[0]

                if body_language_class == "jab" and not box_form[2]:
                    box_form = [False, False, True, False, False, False]

                    send_data("Jab")
                elif body_language_class == "straigth" and not box_form[3]:
                    box_form = [False, False, False, True, False, False]

                    send_data("Straigth")
                elif body_language_class == "left_hook" and not box_form[4]:
                    box_form = [False, False, False, False, True, False]

                    send_data("Left Hook")
                elif body_language_class == "right_hook" and not box_form[5]:
                    box_form = [False, False, False, False, False, True]

                    send_data("Right hook")
                elif body_language_class == "no_guard" and not box_form[0]:
                    box_form = [True, False, False, False, False, False]

                    send_data("No Guard")
                elif body_language_class == "guard" and not box_form[1]:
                    box_form = [False, True, False, False, False, False]

                    send_data("Guard")
            except Exception as e:
                print(f"Error: {e}")

        cv2.imshow('Raw Webcam Feed', image)

        if connected == False:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_ADDRESS, SERVER_PORT))
            connected = True

        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()