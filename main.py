from flask import Flask, render_template, request, session, redirect , url_for, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os
import urllib.request
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import math
import mediapipe as mp
import base64
import tempfile
import time
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///text.db'
app.config['SECRET_KEY'] = '63103453574bccae5541fa05'
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def base64_encode(data):
    return base64.b64encode(data).decode('utf-8')

app.jinja_env.filters['b64encode'] = base64_encode

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    email = db.Column(db.String(), unique = True, nullable = False)
    username = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)

class Img(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    first_img = db.Column(db.Text, nullable=False)
    second_img = db.Column(db.Text, nullable=False)
    analysis = db.Column(db.Text, nullable = False)
    holder = db.Column(db.Text, nullable = False)
    mimetype = db.Column(db.Text, nullable = False)

@app.route("/home")
@app.route("/")

def home():
    return render_template("home.html")


@app.route('/upload', methods=['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        pic = request.files['pic']
        if not pic:
            return 'No pic uploaded', 400
        mp_pose = mp.solutions.pose
        mp_draw = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        ok = 0
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_filename = temp_file.name
            pic.save(temp_filename)
            image1 = cv2.imread(temp_filename)

            with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=2) as pose:
                results = pose.process(cv2.cvtColor(image1, cv2.COLOR_BGR2RGB))
                annotated_image = image1.copy()
                for i in range(11):
                    try:
                        results.pose_landmarks.landmark[i].x = -1
                        ok = 1
                    except:
                        ok = 0
                        
                mp_draw.draw_landmarks(annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                second_img_filename = "annotated.jpg"
                cv2.imwrite(second_img_filename, annotated_image)
        if(ok != 0):
            landmarks = results.pose_landmarks.landmark


            # Define the landmark coordinates
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].z]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].z]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].z]

            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].z]

            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z]
            right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z]

            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].z]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].z]


            for landmark_name in mp_pose.PoseLandmark:
                name = str(landmark_name).replace('PoseLandmark.', '').lower()
                exec(f'{name} = [landmarks[landmark_name].x, landmarks[landmark_name].y, landmarks[landmark_name].z]')





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

            def FeedbackAngle(user_angle, alpha, beta, gamma, text):
                if user_angle >= alpha:
                    return "Amazing"
                elif beta <= user_angle < alpha:
                    return "You are really close. " + text
                else:
                    return "Keep up the hard work! " + text


            def FeedbackPose(users, arrayPose):
                feedback = []
                item = 0
                for ang in arrayPose:
                    result = FeedbackAngle(users[item], 0.9 * ang, 0.8 * ang, 0.7 * ang, message[item])
                    feedback.append(result)
                    item += 1
                return feedback
            analysis = ', '.join(str(item) for item in FeedbackPose(user, arabesque))

        else:
            analysis = "No humans"
        
        time.sleep(5)
        with open(temp_filename, 'rb') as f:
            img_data = f.read()
        mimetype = pic.mimetype
        email = session['email']
        img = Img(first_img=img_data, second_img=open(second_img_filename, 'rb').read(), analysis=analysis, mimetype=mimetype, holder=email)
        db.session.add(img)
        db.session.commit()
        return redirect(url_for('profile'))



    return render_template('upload.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'remember' in session and session['remember'] == True:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            hash_object = hashlib.sha256(password.encode('utf-8'))
            hex_dig = hash_object.hexdigest()
            if user.password == hex_dig:
                session['remember'] = True
                session['email'] = email
                session.permanent = True
                return redirect(url_for('profile'))
            else:
                return render_template("login.html", message = "Invalid Credentials")
        else:
            return render_template("login.html", message = "Invalid Credentials")
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():

    if 'remember' in session and session['remember'] == True:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        psw = request.form.get("password")
        psw_confirm = request.form.get("confirm_password")
        if User.query.filter_by(username=username).first():
            return render_template('register.html', message="Username already exists.")
        if User.query.filter_by(email=email).first():
            return render_template('register.html', message="Another account is using this email.")
        if psw != psw_confirm:
            return render_template('register.html', message="The passwords does not match.")
        hash_object = hashlib.sha256(psw.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        user = User(username=username, email=email, password=hex_dig)
        db.session.add(user)
        db.session.commit()
        session['email'] = email
        session['remember'] = True
        session.permanent = True
    
    return render_template('register.html')

@app.route('/images/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/profile')
def profile():
    email = session['email']
    images = Img.query.filter_by(holder=email).all()
    images.reverse()
    return render_template('profile.html', images=images)


@app.route('/logout')
def logout():
    session.pop("email", None)
    session.pop("remember", None)
    return redirect('/')
if(__name__ == "__main__"):
    app.run(debug=True)