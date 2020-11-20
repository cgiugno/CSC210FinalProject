from flask import Flask, request, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

from forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userlists.db'
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

application = app
bootstrap = Bootstrap(app)
manager = Manager(app)

#Initialize login
login_manager.init_app(app)

#Initialize database
db = SQLAlchemy(app)

#Add migration to database
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)

#Create db User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("home.html")

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST']) 
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You can now login.")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash("Invalid username or password.")
    return render_template("login.html", form=form)

#We can use the @login_required to keep guest users from seeing a page
@app.route('/secret')
@login_required
def secret():
    return "Only authenticated users are allowed!"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))