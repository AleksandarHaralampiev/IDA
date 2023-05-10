import numpy as np
import cv2
import math
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

imagein = "anime-girl-ballet-dancing-5911930.jpg"
image1 = cv2.imread(imagein)

with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=2) as pose:
    results = pose.process(cv2.cvtColor(image1, cv2.COLOR_BGR2RGB))
    annotated_image = image1.copy()
    for i in range(11):
        results.pose_landmarks.landmark[i].x = -1
    mp_draw.draw_landmarks(annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    cv2.imwrite("res.jpg", annotated_image)  # save it

# Second approach: landmark names as variable names and coordinates as values
landmarks = results.pose_landmarks.landmark
for landmark_name in mp_pose.PoseLandmark:
    name = str(landmark_name).replace('PoseLandmark.', '').lower()
    exec(f'{name} = [landmarks[landmark_name].x, landmarks[landmark_name].y, landmarks[landmark_name].z]')


"""angle calculations"""


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def calculate_slope(pointA, pointB, direction):
    if direction == 'vertical':
        return 90 - np.arctan((pointA[1] - pointB[1]) / (pointA[0] - pointB[0])) * 180 / np.pi
    return np.arctan((pointA[1] - pointB[1]) / (pointA[0] - pointB[0])) * 180 / np.pi


def calc_angle_four_points(a, b, c, d):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    d = np.array(d)

    e = a - b
    f = c - d

    cos_angle = (e[0] * f[0] + e[1] * f[1]) / (((e[0] ** 2 + e[1] ** 2) ** 0.5) * ((f[0] ** 2 + f[1] ** 2) ** 0.5))
    angle = np.arccos(cos_angle) * 180 / np.pi
    return angle

                                    
user_left_knee= calculate_angle(left_hip,left_knee,left_ankle)
user_right_knee=calculate_angle(right_hip,right_knee,right_ankle)
user_legs= calc_angle_four_points(right_hip, right_knee, left_hip, left_knee)
user_body=calculate_slope(right_shoulder,right_hip,"horizontal")

user_right_elbow = calculate_angle(right_wrist, right_elbow, right_shoulder)
user_left_elbow = calculate_angle(left_wrist, left_elbow, left_shoulder)
user_right_shoulder = calculate_angle(right_hip, right_shoulder, right_elbow)
user_left_shoulder = calc_angle_four_points(left_shoulder, left_hip, left_shoulder, left_elbow)

user=np.array([user_left_knee,user_right_knee,user_legs,user_body])
message=["Keep your left leg straight","Keep your right leg straight","Lift your leg higher", "Lift your body"]
arabesque= np.array([174.1, 179.5, 92.2, 70.5]) # ["Keep your left leg straight","Keep your right leg straight","Lift your leg higher", "Lift your body"])

"""Feedback"""

def FeedbackAngle(user_angle,alpha, beta, gama, text): #1. user_angle- calculated angle, 2. alpha- desired angle, 3.beta - okay angle, 4. gama- bad angle, text- personal feedback text
  if (user_angle>=alpha):
    print("Amazing")
  elif (alpha>user_angle>=beta):
    print("You are really close."+ text)
  else :
    print( "Keep up the hard work!"+text)
    

def FeedbackPose(users,arrayPose):
  item=0
  for ang in arrayPose:
    FeedbackAngle(users[item], 0.9*ang,0.8*ang,0.7*ang,message[item])
    item=item+1
    
FeedbackPose(user, arabesque)