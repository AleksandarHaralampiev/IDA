from flask import Flask, render_template, request, session, redirect , url_for, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os
import urllib.request
from werkzeug.utils import secure_filename

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

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    email = db.Column(db.String(), unique = True, nullable = False)
    username = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)


@app.route("/home")
@app.route("/")

def home():
    return render_template("home.html")

@app.route('/upload', methods=['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Image successfully uploaded and displayed below')
            return render_template('upload.html', filename=filename)
        else:
            flash('Allowed image types are - png, jpg, jpeg')
            return redirect(request.url)
    return render_template('upload.html')

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)



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
@app.route('/profile')
def profile():
    return render_template('profile.html')
if(__name__ == "__main__"):
    app.run(debug=True)