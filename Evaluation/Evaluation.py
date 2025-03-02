import os
import warnings
import time
import cv2
import pandas as pd
import numpy as np
import pickle

import csv
import datetime

import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
PINK = (98, 57, 237)
PURPLE = (105, 40, 32)

class PoseController:
    def __init__(self, model_path) -> None:
        
        self.isNotJab = True
        self.isNotStraight = True
        self.isNotLeftHook = True
        self.isNotRightHook = True
        self.isNotLeftUppercut = True
        self.isNotRightUppercut = True
        self.isNotGuard = True
        self.isNotGuardLeftBody = True
        self.isNotGuardRightBody = True
        self.isNotIdle = True

        # Avoid
        self.isSlipLeft = False
        self.isSlipRight = False
        self.isDucking = False
        self.isPause = False

        "=== Scenario ==="
        self.pose_counter = 0
        self.recent_pose = None
        self.condition = []
        self.pose_detected = []
        self.pose_sequence = []
        
        "=== Load Model ==="
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def draw_horizontal_panel(self, image, shoulderR, shoulderL, nose):
        height, width, _ = image.shape
        
        left_line = (int(shoulderL.x * width) - 10, 0), (int(shoulderL.x * width) - 10, height)
        right_line = (int(shoulderR.x * width) + 10, 0), (int(shoulderR.x * width) + 10, height)
        
        noseX = nose.x * width
        noseRight = left_line[0][0] - (noseX)
        noseLeft = right_line[0][0] - (noseX)   
        
        if noseRight > 0 and not self.isSlipRight:
            self.send_data("Slip_Right")
            self.update_pose_detection(SlipR=True)
        elif noseLeft < 0 and not self.isSlipLeft:
            self.send_data("Slip_Left")
            self.update_pose_detection(SlipL=True)
        elif not noseRight > 0 and not noseLeft < 0:
            self.isSlipLeft = False
            self.isSlipRight = False
            

        cv2.line(image, left_line[0], left_line[1], GREEN, 3)
        cv2.line(image, right_line[0], right_line[1], GREEN, 3)

        return left_line, right_line
    
    def draw_vertical_panel(self, image, nose, hip, elbow_l, elbow_r):
        height, width, _ = image.shape
        top_offset = 25
        bottom_offset = 120

        noseY = int(nose.y * height)
        hipY = int(hip.y * height)

        elbowL_y = int(elbow_l.y * height)
        elbowR_y = int(elbow_r.y * height)

        hip_elbowL = elbowL_y - hipY + 70
        # print("hip_elbowL :", hip_elbowL)
        hip_elbowR = elbowR_y - hipY + 70
        # print("hip_elbowR :", hip_elbowR)

        if not self.isDucking:
            if hip_elbowL > 0  or hip_elbowR > 0:
                if hip_elbowL > 0 and hip_elbowR > 0:
                    if hip_elbowL > hip_elbowR and self.isNotGuardLeftBody:
                        try:
                            # self.send_data("Guard_LeftBody")
                            self.update_pose_detection(GuardLeftBody=False)
                        except Exception as e:
                            print(e)
                    elif hip_elbowR > hip_elbowL and self.isNotGuardRightBody:
                        # self.send_data("Guard_RightBody")
                        self.update_pose_detection(GuardRightBody=False)
                elif hip_elbowL > 0 and self.isNotGuardLeftBody:
                    # self.send_data("Guard_LeftBody")
                    self.update_pose_detection(GuardLeftBody=False)
                elif hip_elbowR > 0 and self.isNotGuardRightBody:
                    # self.send_data("Guard_RightBody")
                    self.update_pose_detection(GuardRightBody=False)
            elif hip_elbowL < 0 and hip_elbowR < 0:
                self.isNotGuardLeftBody = True
                self.isNotGuardRightBody = True
    
        hip_line = (0, hipY - 70), (width, hipY - 70)
        top_y = (0, noseY - 130), (width, noseY - 130)
        bottom_y = (0, noseY + 260), (width, noseY + 260)

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
                self.isDucking = True
                # bottom_line = (0, (noseY + maxBottom ) + bottom_offset), (width, (noseY + maxBottom) + bottom_offset)
            else:
                top_line = (0, noseY + top_offset), (width, noseY + top_offset)
                bottom_line = (0, noseY + bottom_offset), (width, noseY + bottom_offset)
                self.isDucking = False

        cv2.line(image, top_line[0], top_line[1], GREEN, 3)
        cv2.line(image, bottom_line[0], bottom_line[1], GREEN, 3)

        cv2.line(image, top_y[0], top_y[1], RED, 2)
        cv2.line(image, bottom_y[0], bottom_y[1], RED, 2)

        cv2.line(image, hip_line[0], hip_line[1], RED, 1)

        return top_line, bottom_line

    def draw_line_and_calculate_gap(self, image, start_point, end_point):
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
        
    def update_pose_detection(self, Jab = True, Straight = True, LeftHook = True,
                        RightHook = True, LeftUppercut = True,
                        RightUppercut = True, Guard = True, Idle = True,
                        GuardLeftBody = True, GuardRightBody = True, SlipL = False, SlipR = False):
    
        self.isNotJab = Jab
        self.isNotStraight = Straight
        self.isNotLeftHook = LeftHook
        self.isNotRightHook = RightHook
        self.isNotLeftUppercut = LeftUppercut
        self.isNotRightUppercut = RightUppercut
        self.isNotGuard = Guard
        self.isNotGuardLeftBody = GuardLeftBody
        self.isNotGuardRightBody = GuardRightBody
        self.isNotIdle = Idle
        self.isSlipLeft = SlipL
        self.isSlipRight = SlipR
    
    def send_prediction(self, body_language_class, prob):

        prediction = f"{body_language_class} : {prob}"
        if body_language_class == "Jab" and self.isNotJab:
            if self.isDucking and prob > 0.70:
                self.send_data("Low_Jab")
                self.update_pose_detection(Jab=False)
            elif not self.isDucking and prob > 0.8:
                self.send_data("Jab")
                self.update_pose_detection(Jab=False)
                print(prediction)
                
    
                        
        elif body_language_class == "Straight" and self.isNotStraight:
            if self.isDucking and prob > 0.78:
                self.send_data("Low_Straight")
                self.update_pose_detection(Straight=False)
                
            elif not self.isDucking and prob > 0.78:
                self.send_data("Straight")        
                self.update_pose_detection(Straight=False)
                
            # print(prediction)
                        
        elif body_language_class == "Left_Hook" and self.isNotLeftHook:
            if self.isDucking and prob > 0.70:
                self.send_data("Left_BodyHook")
                self.update_pose_detection(LeftHook=False)
                
            elif not self.isDucking and prob > 0.78:
                self.send_data("Left_Hook")
                self.update_pose_detection(LeftHook=False)
                
            # print(prediction)
            

        elif body_language_class == "Right_Hook" and self.isNotRightHook:
            if self.isDucking and prob > 0.70:
                self.send_data("Right_BodyHook")
                self.update_pose_detection(RightHook=False)
                
                
            elif not self.isDucking and prob > 0.78:
                self.send_data("Right_Hook")
                self.update_pose_detection(RightHook=False)
                
            # print(prediction)
            

        elif body_language_class == "Left_Uppercut" and self.isNotLeftUppercut and prob > 0.78:
            self.update_pose_detection(LeftUppercut=False)
            self.send_data("Left Uppercut")
            # print(prediction)

            

        elif body_language_class == "Right_Uppercut" and self.isNotRightUppercut and prob > 0.78:
            self.update_pose_detection(RightUppercut=False)
            self.send_data("Right_Uppercut")
            # print(prediction)

            

        elif body_language_class == "Guard" and self.isNotGuard and prob > 0.78:
            self.update_pose_detection(Guard=False)
            self.send_data("Guard")
            # print(prediction)

            

        elif body_language_class == "Idle" and self.isNotIdle and prob > 0.78:
            self.update_pose_detection(Idle=False)
            self.send_data("Idle")
            # print(prediction)

        else:
            pass

    def send_data(self, value):
        if value != self.recent_pose:
            print(value)
            self.recent_pose = value
            
            self.condition.append(self.pose_sequence[self.pose_counter] == self.recent_pose)
            self.pose_detected.append(self.recent_pose)

            print(self.recent_pose, self.pose_counter)
            self.pose_counter += 1

    def evaluating(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') 

        with open('Scenario/scenario_2.csv', 'r') as csvfile, open(f'Tested/{timestamp}.csv', 'w', newline='') as outfile:
            reader = csv.reader(csvfile)
            data = list(reader)
            writer = csv.writer(outfile)

            for row in data:
                scenario = row[0]
                file = row[1]
                pose = row[2:]

                evaluated = self.run(file, len(pose), pose)
                print(evaluated)
            
                modified_row = row + ['detected'] + evaluated[0] + ['condition'] + evaluated[1]
                writer.writerow(modified_row) 

    def run(self, file, pose_limit, poses):
        time.sleep(1)
        
        self.pose_counter = 0
        self.recent_pose = None
        self.pose_sequence = poses
        self.condition = []
        self.pose_detected = []

        print(pose_limit)

        cap = cv2.VideoCapture(f"Scenario/{file}")
        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic :

            while cap.isOpened():
                ret, frame = cap.read()

                # Recolor Feed
                try:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False        
                    
                    # Make Detections
                    results = holistic.process(image)

                    # Recolor image back to BGR for rendering
                    image.flags.writeable = True   
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                except Exception as e:
                    print(e)

                try:
                    # Get specific landmarks
                    nose = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.NOSE]
                    wrist_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_WRIST]
                    elbow_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_ELBOW]
                    wrist_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_WRIST]
                    elbow_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_ELBOW]

                    # Use For Making Guideline Purpose
                    shoulder_l = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_SHOULDER]
                    shoulder_r = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_SHOULDER]
                    hip = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_HIP]


                    show_landmark_list = landmark_pb2.NormalizedLandmarkList()
                    show_landmark_list.landmark.extend([nose, wrist_l, wrist_r, elbow_l, elbow_r, hip])
                    
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
                    
                    left_line, right_line = self.draw_horizontal_panel(image, shoulder_l, shoulder_r, nose)
                    top_line, bottom_line = self.draw_vertical_panel(image, nose, hip, elbow_l, elbow_r)
                    
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
                    
                    cv2.line(image, wristL_horGap[0], wristL_horGap[1], PINK, 4)
                    cv2.line(image, wristL_horGap[0], (right_line[0][0], wristL_y + 20), PINK, 4)

                    # Vertical Gap
                    wristL_topLine = wristL_y - top_line[0][1]
                    wristL_bottomLine = bottom_line[0][1] - wristL_y


                    cv2.line(image, wristL_verGap[0], wristL_verGap[1] , PURPLE, 4)
                    cv2.line(image, wristL_verGap[0], (wristL_x, bottom_line[0][1]), PURPLE, 4)
                    
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

                    cv2.line(image, wristR_horGap[0], wristR_horGap[1] , PINK, 4)
                    cv2.line(image, wristR_horGap[0], (left_line[0][0], wristR_y + 20) , PINK, 4)

                    #Vertical Gap
                    wristR_topLine = wristR_y - top_line[0][1]
                    wristR_bottomLine = bottom_line[0][1] - wristR_y

                    cv2.line(image, wristR_verGap[0], wristR_verGap[1], PURPLE, 4)
                    cv2.line(image, wristR_verGap[0], (wristR_x, bottom_line[0][1]), PURPLE, 4)

                    wristRight_leftTopLine_landmark = landmark_pb2.NormalizedLandmark()
                    wristRight_leftTopLine_landmark.x = wristR_leftLine
                    wristRight_leftTopLine_landmark.y = wristR_topLine

                    wristRight_rightBottomLine_landmark = landmark_pb2.NormalizedLandmark()
                    wristRight_rightBottomLine_landmark.x = wristR_rightLine    
                    wristRight_rightBottomLine_landmark.y = wristR_bottomLine

                    # Drawing line and calculating gap for left wrist
                    gap_nose_left = self.draw_line_and_calculate_gap(image, nose, wrist_l)

                    # Drawing line and calculating gap for right wrist
                    gap_nose_right = self.draw_line_and_calculate_gap(image, nose, wrist_r)

                    new_lm = landmark_pb2.NormalizedLandmarkList()
                    new_lm.landmark.extend([wrist_l, wrist_r, elbow_l, elbow_r,
                                            gap_nose_right, gap_nose_left, 
                                            wristLeft_leftTopLine_landmark, wristLeft_rightBottomLine_landmark, 
                                            wristRight_leftTopLine_landmark, wristRight_rightBottomLine_landmark
                                            ])
                except Exception as e:
                    print(e)

                try:
                    pose = new_lm.landmark
                    pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())

                    detected_pose = pd.DataFrame([pose_row])
                    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

                    body_language_class = self.model.predict(detected_pose)[0]
                    body_language_prob = self.model.predict_proba(detected_pose)[0]

                    prob = round(body_language_prob[np.argmax(body_language_prob)],2)

                    if not self.isSlipLeft and not self.isSlipRight and self.isNotGuardLeftBody and self.isNotGuardRightBody:
                        self.send_prediction(body_language_class, prob)
                    
                    if self.pose_counter == pose_limit:
                        cap.release()
                        cv2.destroyAllWindows()
                        return self.pose_detected, self.condition 
                    
                except Exception as e:
                    pass

                cv2.imshow('Raw Webcam Feed', image)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    PoseController("v1_rf_model.pkl").evaluating()