from flask import Flask, render_template, url_for, request, redirect, flash
from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from datetime import datetime

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

from forms import LoginForm, RegisterForm, EditProfileForm

app = Flask(__name__)
application = app

#Initialize Bootstrap, Manager
bootstrap = Bootstrap(app)
manager = Manager(app)

#Setup SQLDatabase name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Configure Login Settings
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

#Initialize the database
db = SQLAlchemy(app)

#Naming convention to enable batch migrations
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

#Add migration to database
migrate = Migrate(app, db, render_as_batch=True)
manager.add_command("db", MigrateCommand)

#Create db User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Tasks', backref='user', lazy="dynamic")

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

#Create Database model/class
class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    #Create a function to return a string to return a string when we add something to db
    def __repr__(self):
        return '<Task %r>' % self.id

#initialize database
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        
        new_task = Tasks(content=task_content, user=current_user._get_current_object())

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/') #for DigScholar this will be 'return redirect('/final')
        except:
            return 'There was an issue adding your task :('
    
    else:
        tasks = Tasks.query.order_by(Tasks.date_created).all()
        return render_template('index.html', tasks=tasks)
    
    if request.method == 'GET':
        pass

    return render_template('index.html')


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Tasks.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/') #for DigScholar this will be 'return redirect('/final')

    except:
        return 'There was an error deleting that task'


@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    task = Tasks.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']


        try:
            db.session.commit()
            return redirect('/') #for DigScholar this will be 'return redirect('/final')
        except:
            return 'There was an issue updating your task :('

    else:
        return render_template('update.html', task=task)



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
            login_user(user, form.remember_user.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash("Invalid username or password.")
    return render_template("login.html", form=form)
#Current logins are:
# Email: dustychirpchirp@gmail.com
# Username: Dusty
# Password: dusty
#And
# Email: fluffyhoneypot@gmail.com
# Username: Fluffy
# Password: fluffy
#(They're both named after my birds -- Katie)

@app.route("/about", methods=["GET","POST"]) 
@login_required
def about():
    return render_template("about.html")

@app.route("/about/edit", methods=["GET", "POST"])
@login_required
def about_edit():
    form = EditProfileForm()
    if form.validate_on_submit():
        user = current_user._get_current_object()
        if form.edit_username.data != "":
            user.username = form.edit_username.data
        if form.edit_email.data != "":
            user.email = form.edit_email.data
        if user.verify_password(form.original_password.data):
            user.password = form.new_password.data
        db.session.commit()
        return redirect(url_for("about"))
    return render_template("edit_about.html", form=form)

#We can use the @login_required to keep guest users from seeing a page
@app.route('/secret')
@login_required
def secret():
    return "Only authenticated users are allowed!"

#Instantiates user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)
    manager.run()
