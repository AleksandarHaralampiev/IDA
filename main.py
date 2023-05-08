from flask import Flask, render_template, request, session, redirect , url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///text.db'
app.config['SECRET_KEY'] = '63103453574bccae5541fa05'
db = SQLAlchemy(app)


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