from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap

app = Flask(__name__)

application = app
bootstrap = Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("home.html")