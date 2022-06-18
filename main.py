from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
import os
from forms import AddCafeForm, RegisterForm, LoginForm
from dotenv import load_dotenv
from flask import session
from functools import wraps
from flask import abort
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECURITY_KEY")


Bootstrap(app)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASES_URL', 'sqlite:///cafes.db')


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
base = declarative_base()
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


class Cafe(db.Model):
    __tablename__ = "cafe_posts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, default=False, nullable=False)
    has_toilet = db.Column(db.Boolean, default=False, nullable=False)
    has_wifi = db.Column(db.Boolean, default=False, nullable=False)
    can_take_calls = db.Column(db.Boolean, default=False, nullable=False)
    seats = db.Column(db.String(250), nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  
    author = relationship('User', back_populates="posts") 
    
db.create_all()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    posts = relationship('Cafe', back_populates="author")


db.create_all()



@app.route('/')
def home():
    

    return render_template('index.html')


ROWS_PER_PAGE=5
@app.route('/all/<int:page_num>', methods=['GET', 'POST'])  # get
def all_cafe(page_num):
    pages = Cafe.query.paginate(page=page_num, per_page = ROWS_PER_PAGE, error_out=True )
    
    return render_template('all.html', pages=pages)



@app.route('/cafe/<int:cafe_id>', methods=['GET', 'POST'])
def show_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    return render_template('cafe.html', cafe=cafe)



@app.route('/add', methods=["GET", "POST"])
@login_required
def add_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
       
        if form.has_sockets.data:
            sockets = 1
        else:
            sockets = 0

        if form.has_wifi.data:
            wifi = 1
        else:
            wifi = 0

        if form.has_toilet.data:
            toilet = 1
        else:
            toilet = 0

        if form.can_take_calls.data:
            take_calls = 1
        else:
            take_calls = 0

        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.name.data,
            location=form.name.data,
            img_url=form.name.data,
            has_sockets=sockets,
            has_wifi=wifi,
            has_toilet=toilet,
            can_take_calls=take_calls,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
        )

        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('all_cafe'))
    print(form.validate_on_submit())
    print(form.errors)
    return render_template('make.html', form=form)


@app.route('/update/<int:cafe_id>', methods=["GET", "POST"])
@login_required
def update(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    # to pre-populate the previous data of cafe
    edit_form = AddCafeForm(obj=cafe)

    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.map_url = edit_form.map_url.data
        cafe.location = edit_form.location.data
        cafe.img_url = edit_form.img_url.data
        cafe.has_sockets = edit_form.has_sockets.data
        cafe.has_wifi = edit_form.has_wifi.data
        cafe.has_toilet = edit_form.has_toilet.data
        cafe.can_take_calls = edit_form.can_take_calls.data
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = edit_form.coffee_price.data

        db.session.commit()
        return redirect(url_for('show_cafe', cafe_id=cafe.id))

    return render_template('make.html', form=edit_form, is_edit=True, cafe=cafe)


@app.route('/delete/<int:cafe_id>', methods=["GET", "POST"])
@login_required
def delete(cafe_id):

    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('all_cafe'))


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first() 
        if user:  
            flash('Email address already exists')
            return redirect(url_for('register'))

        new_user = User(name=name,
                        email=email,
                        password=generate_password_hash(password,
                                                        method="pbkdf2:sha256",
                                                        salt_length=8))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()
        name = user.name

        if not user:
            flash("Email Doesnot exist, Please check your data")
            return redirect(url_for('login'))
        if not check_password_hash(user.password, password):
            flash("Incorrect Password, Check again!")
            return redirect(url_for('login'))
       
        login_user(user, remember=remember)

        return render_template('index.html', name=current_user.name)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

#host="192.168.68.107", port=5000,