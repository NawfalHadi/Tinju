import pickle
import warnings
import datetime
import numpy as np
import pandas as pd
import csv
import time
import os

import cv2
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2

mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions


" Offset value should be based on the size of player detection "
offset = 10 # temp value

line_thickness = 2
line_color = (0, 255, 0)  # Green color
line_color_red = (0, 0, 255)  # Red color
line_color_blue = (255, 0, 0)  # Blue color

with open("v3_model.pkl", 'rb') as f:
    model = pickle.load(f)


def draw_horizontal_panel(image, shoulderR, shoulderL):
    height, width, _ = image.shape
    
    left_line = (int(shoulderL.x * width) - offset, 0), (int(shoulderL.x * width) - offset, height)
    right_line = (int(shoulderR.x * width) + offset, 0), (int(shoulderR.x * width) + offset, height)
    
    cv2.line(image, left_line[0], left_line[1], line_color, line_thickness)
    cv2.line(image, right_line[0], right_line[1], line_color, line_thickness)

    return left_line, right_line

def draw_vertical_panel(image, nose):
    height, width, _ = image.shape
    top_offset = 25
    bottom_offset = 120

    noseY = int(nose.y * height)

    top_y = (0, noseY - 130), (width, noseY - 130)
    bottom_y = (0, noseY + 240), (width, noseY + 240)

    maxHeight = top_y[0][1]
    maxBottom = int(height) - int(bottom_y[0][1])

    if (maxHeight < 0):
        # print("Log : Paused Game")
        top_line = (0, (noseY  + maxHeight) + top_offset ), (width, (noseY + maxHeight) + top_offset)
        bottom_line = (0, noseY + bottom_offset), (width, noseY + bottom_offset)
        # bottom_line = (0, (noseY  + maxHeight) + bottom_offset ), (width, maxHeight - bottom_offset)
    else:
        # print("Log : Game Running")
        
        if(maxBottom < 0):
            # print("Log : Duck")
            top_line = (0, (noseY + maxBottom )), (width, (noseY + maxBottom))
            bottom_line = (0, noseY + bottom_offset), (width, noseY + bottom_offset)
            # bottom_line = (0, (noseY + maxBottom ) + bottom_offset), (width, (noseY + maxBottom) + bottom_offset)
        else:
            top_line = (0, noseY + top_offset), (width, noseY + top_offset)
            bottom_line = (0, noseY + bottom_offset), (width, noseY + bottom_offset)

    cv2.line(image, top_line[0], top_line[1], line_color_blue, line_thickness)
    cv2.line(image, bottom_line[0], bottom_line[1], line_color_blue, line_thickness)

    cv2.line(image, top_y[0], top_y[1], line_color_red, line_thickness)
    cv2.line(image, bottom_y[0], bottom_y[1], line_color_red, line_thickness)

    return top_line, bottom_line

def draw_line_and_calculate_gap(image, start_point, end_point):
    if start_point and end_point:
        x1, y1 = start_point.x * image.shape[1], start_point.y * image.shape[0]
        x2, y2 = end_point.x * image.shape[1], end_point.y * image.shape[0]
        
        # Calculate normalized coordinates
        gap_x = (x2 - x1) / image.shape[1]
        gap_y = (y2 - y1) / image.shape[0]

        # Draw line
        x1, y1 = int(x1), int(y1)
        x2, y2 = int(x2), int(y2)
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)

        gap_landmark = landmark_pb2.NormalizedLandmark()
        gap_landmark.x = gap_x
        gap_landmark.y = gap_y

        return gap_landmark
    else:
        return None

# cap = cv2.VideoCapture("../Evaluation/Scenario/scenario_2.mp4")
cap = cv2.VideoCapture(0)
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic :

    while cap.isOpened():
        ret, frame = cap.read()

        # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False        
        
        # Make Detections
        results = holistic.process(image)

        # Recolor image back to BGR for rendering
        image.flags.writeable = True   
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Get specific landmarks
        nose = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.NOSE]
        wrist_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_WRIST]
        elbow_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_ELBOW]
        wrist_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_WRIST]
        elbow_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_ELBOW]

        # Use For Making Guideline Purpose
        shoulder_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_SHOULDER]
        shoulder_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_SHOULDER]

        show_landmark_list = landmark_pb2.NormalizedLandmarkList()
        show_landmark_list.landmark.extend([nose, wrist_l, wrist_r, elbow_l, elbow_r])
        
        # Draw landmarks
        for landmark in show_landmark_list.landmark:
            x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
        cv2.circle(image, (x, y), 5, (255, 0, 0), -1)

        """
        IT GIVES THE LOCATION OF THE CENTER BASED OFF 
        THE NOSE X,Y FROM THE FRAMES
        """

        # nose_x, nose_y = int(nose.x * image.shape[1]), int(nose.y * image.shape[0])
        
        wristL_x, wristL_y = int(wrist_l.x * image.shape[1]), int(wrist_l.y * image.shape[0])
        wristR_x, wristR_y = int(wrist_r.x * image.shape[1]), int(wrist_r.y * image.shape[0])
        
        left_line, right_line = draw_horizontal_panel(image, shoulder_l, shoulder_r)
        top_line, bottom_line = draw_vertical_panel(image, nose)
        
        # Below this is temporary for drawing the line, and we need the calculation of the gap
        wristL_horGap = (wristL_x, wristL_y), (left_line[0][0], wristL_y)
        wristR_horGap = (wristR_x, wristR_y), (right_line[0][0], wristR_y)
        
        wristL_verGap = (wristL_horGap[0]), (wristL_x, top_line[0][1])
        wristR_verGap = (wristR_horGap[0]), (wristR_x, top_line[0][1])

        left_line_x, left_line_y = wristL_horGap[1]
        right_line_x, right_line_y = wristR_horGap[1]
        

        " Wrist Left "
        
        wristL_x, wristL_y = wristL_horGap[0]

        # Horizontal Gap
        # make it so it has a (+ and - value)
        wristL_leftLine = wristL_x - left_line_x
        wristL_rightLine = wristL_x -right_line_x
         
        cv2.line(image, wristL_horGap[0], wristL_horGap[1], line_color_blue, line_thickness)
        cv2.line(image, wristL_horGap[0], (right_line[0][0], wristL_y + 20), line_color_red, line_thickness)

        # Vertical Gap
        wristL_topLine = wristL_y - top_line[0][1]
        wristL_bottomLine = bottom_line[0][1] - wristL_y

        cv2.line(image, wristL_verGap[0], wristL_verGap[1] ,line_color_red, line_thickness)
        cv2.line(image, wristL_verGap[0], (wristL_x, bottom_line[0][1]), line_color_red, line_thickness)
        
        wristLeft_leftTopLine_landmark = landmark_pb2.NormalizedLandmark()
        wristLeft_leftTopLine_landmark.x = wristL_leftLine
        wristLeft_leftTopLine_landmark.y = wristL_topLine

        wristLeft_rightBottomLine_landmark = landmark_pb2.NormalizedLandmark()
        wristLeft_rightBottomLine_landmark.x = wristL_rightLine
        wristLeft_rightBottomLine_landmark.y = wristL_bottomLine

        " Wrist Right "
        wristR_x, wristR_y = wristR_horGap[0]

        # Horizontal Gap
        wristR_leftLine = wristR_x - left_line_x
        wristR_rightLine = wristR_x - right_line_x

        cv2.line(image, wristR_horGap[0], wristR_horGap[1] , line_color_blue, line_thickness)
        cv2.line(image, wristR_horGap[0], (left_line[0][0], wristR_y + 20) , line_color_red, line_thickness)

        #Vertical Gap
        wristR_topLine = wristR_y - top_line[0][1]
        wristR_bottomLine = bottom_line[0][1] - wristR_y

        cv2.line(image, wristR_verGap[0], wristR_verGap[1], line_color_red, line_thickness)
        cv2.line(image, wristR_verGap[0], (wristR_x, bottom_line[0][1]), line_color_red, line_thickness)

        wristRight_leftTopLine_landmark = landmark_pb2.NormalizedLandmark()
        wristRight_leftTopLine_landmark.x = wristR_leftLine
        wristRight_leftTopLine_landmark.y = wristR_topLine

        wristRight_rightBottomLine_landmark = landmark_pb2.NormalizedLandmark()
        wristRight_rightBottomLine_landmark.x = wristR_rightLine
        wristRight_rightBottomLine_landmark.y = wristR_bottomLine

        # Drawing line and calculating gap for left wrist
        gap_nose_left = draw_line_and_calculate_gap(image, nose, wrist_l)

        # Drawing line and calculating gap for right wrist
        gap_nose_right = draw_line_and_calculate_gap(image, nose, wrist_r)

        gap_hand_left = draw_line_and_calculate_gap(image, elbow_l, wrist_l)
        gap_hand_right = draw_line_and_calculate_gap(image, elbow_r, wrist_r)

        new_lm = landmark_pb2.NormalizedLandmarkList()
        new_lm.landmark.extend([wrist_l, wrist_r, elbow_l, elbow_r,
                                gap_nose_right, gap_nose_left, 
                                wristLeft_leftTopLine_landmark, wristLeft_rightBottomLine_landmark, 
                                wristRight_leftTopLine_landmark, wristRight_rightBottomLine_landmark
                                ])

        try:
            pose = new_lm.landmark
            pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())

            pose_detected = pd.DataFrame([pose_row])
            warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

            body_language_class = model.predict(pose_detected)[0]
            body_language_prob = model.predict_proba(pose_detected)[0]

            prob = round(body_language_prob[np.argmax(body_language_prob)],2)

            if prob > 0.70:
                print(body_language_class, str(round(body_language_prob[np.argmax(body_language_prob)],2)))
            
        except Exception as e:
            pass
        cv2.imshow('Raw Webcam Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()