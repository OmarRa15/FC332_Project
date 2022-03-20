from flask import Flask
from os import environ
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SECRET_KEY'] = environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL'][0:8] + 'ql' + environ['DATABASE_URL'][8:]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from sql_models import db, StdUsers
from forms import StdLoginForm, StdRegisterForm

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

Bootstrap(app)

@loginManager.user_loader
def load_user(user_id):
    return StdUsers.query.get(int(user_id))


@app.route('/stdSignup', methods=['GET', 'POST'])
def StdSignup():
    if current_user.is_authenticated:
        return redirect('/')
    form = StdRegisterForm()

    if form.validate_on_submit():
        password = form.password.data
        hashedPass = generate_password_hash(password, method='sha256')

        newUser = StdUsers(first_name=form.first_name.data, last_name=form.last_name.data, password=hashedPass,
                           std_id=form.std_id.data)

        db.session.add(newUser)
        db.session.commit()

        flash("Signed Up Successfully!!")
        return redirect(url_for('stdLogin'))
    return render_template('signup.html', form=form)


@app.route('/stdLogin', methods=['GET', 'POST'])
def stdLogin():
    if current_user.is_authenticated:
        return redirect('/')
    form = StdLoginForm()
    if form.validate_on_submit():
        user = StdUsers.query.filter_by(std_id=form.studentID.data).first()

        # if not user.is_confirmed:
        #     return '<h1 style= "text-align: center">Your Email hasn\'t been confirmed yet,' \
        #            '\nPlease <a href="{}">click here</a> to confirm your email <h1>' \
        #         .format(url_for('send_confirmation', email=user.email, _external=True))
        login_user(user, remember=form.remember.data)
        return "LOGGED IN!!"
        # return redirect('/')

    return render_template('login.html', form=form)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
