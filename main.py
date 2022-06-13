from flask import Flask , render_template, request,url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditorField
import os
# from dotenv import load_dotenv

app=Flask(__name__)

# load_dotenv(r"E:\PYTHON_BOOTCAMP_Dr_ANGELA_YU\NomadCafe\.env")
app.config['SECURITY_KEY'] ="asrMCI8764268mahsgvg;.v'aviy87945" # os.environ.get("SECURITY_KEY")

Bootstrap(app)

@app.route('/')
def home():
    #add button for show_cafe
    return render_template('index.html')

@app.route('/all')
def all_cafe():
    #use databse query all
    return render_template('all.html')


@app.route('/cafe/<cafe-id::int>')
def show_cafe():
    return render_template('cafe.html')
@app.route('/add')
def add_cafe():
    #use wtforms to add post request for add in db
    return render_template('make.html')

@app.route('/update/<cafe-id::int>')
def update():
    #from update button clicked in  cafe htmlredirected to add html but refractor title as edit also use ckeditor
    # to load and fill automatically the previuos version od cafe details in reapective place
    return render_template('make.html')

@app.route('register')
def register():
    return render_template('register.html')

@app.route('login')
def login():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(host="192.168.68.101", port=5000, debug=True)