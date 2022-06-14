from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
import os
from forms import AddCafeForm, RegisterForm, LoginForm
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv(r"E:\PYTHON_BOOTCAMP_Dr_ANGELA_YU\NomadCafe\.env")
app.config['SECRET_KEY'] = os.environ.get("SECURITY_KEY")

# FOR BOOTSTRAP EXTENSION
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'sqlite:///cafes.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)


#  you need to specify the user loader. A user loader tells Flask-Login how to find a specific user from the
#  ID that is stored in their session cookie.
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


class Cafe(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, default=False, nullable=False)
    has_toilet = db.Column(db.Boolean, default=False, nullable=False)
    has_wifi = db.Column(db.Boolean, default=False, nullable=False)
    can_take_calls = db.Column(db.Boolean, default=False, nullable=False)
    seats = db.Column(db.String(250), nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)


# The UserMixin will add Flask-Login attributes to the model so that Flask-Login will be able to work with it
class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)


# db.create_all()
# INSERT THE ENTRIES TO CREATE A TABLE POPULATED WITH CAFE DETAILS


@app.route('/')
def home():
    # add button for show_cafe
    return render_template('index.html')


# TODO -1 GET ALL CAFE IN /all USING QUERY.ALL AND GET METHODS

@app.route('/all', methods=['GET', 'POST'])  # get
def all_cafe():
    cafes = Cafe.query.all()
    return render_template('all.html', cafes=cafes)


# TODO -2 GET A CAFE ON CLICKING CAFE NAME, TAKES TO SEPEARATE PAGE TO SHOW INDIVIDUAL CAFE DETAILS
@app.route('/cafe/<int:cafe_id>', methods=['GET', 'POST'])
def show_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    return render_template('cafe.html', cafe=cafe)


# TODO -3 TO ADD CAFE USING WTFORMS BOOTSTRAP, CREATE FORM.PY AND USE POST METHOD RECEIVE THE DATA AND ADD TO DB &
#  COMMIT
@app.route('/add', methods=["GET", "POST"])
@login_required
def add_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        # SINCE DB HAS NO BOOLEAN TYPE, 1 IS FOR tRUE, 0 IS FALSE, IN WTFORM BOOLEAN IS T/F HENCE CONVERTING TRUE TO
        # 1 AS THE DB CAN UNDERSTAND
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

    # name=cafe.name,
    #     map_url=cafe.map_url,
    #
    #     location=cafe.location,
    #     img_url=cafe.img_url,
    #     has_sockets=cafe.has_sockets,
    #     has_wifi=cafe.has_wifi,
    #     has_toilet=cafe.has_toilet,
    #     can_take_calls=cafe.can_take_calls,
    #     seats=cafe.seats,
    #     coffee_price=cafe.coffee_price
    # )
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

        user = User.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
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

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            flash("Email Doesnot exist, Please check your data")
            return redirect(url_for('login'))
        if not check_password_hash(user.password, password):
            flash("Incorrect Password, Check again!")
            return redirect(url_for('login'))
        # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        # Finally, add the login_user function before redirecting to the profile page to create the session:
        login_user(user, remember=remember)
        # if the above check passes, then we know the user has the right credentials
        return render_template('index.html', name=current_user.name)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host="192.168.68.101", port=5000, debug=True)

    # flash wrong url, cafe deleted cafe updated, registered, logout login
