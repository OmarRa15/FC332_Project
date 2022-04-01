from flask import Flask, abort
from os import environ
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SECRET_KEY'] = environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL'][0:8] + 'ql' + environ['DATABASE_URL'][8:]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from sql_models import db, User, Student, Advisor, Application
from forms import StdRegisterForm, AdvRegisterForm, ApplicationForm, ViewApplicationForm, LoginForm

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'landing'

Bootstrap(app)


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/stdSignup', methods=['GET', 'POST'])
def stdSignup():
    if current_user.is_authenticated:
        if current_user.type_ == 'student':
            return redirect('/student')
        elif current_user.type_ == 'advisor':
            return redirect('/advisor')
    form = StdRegisterForm()

    if form.validate_on_submit():
        password = form.password.data
        hashedPass = generate_password_hash(password, method='sha256')
        advisor_email = str(form.advisor.data).lower()
        newUser = Student(first_name=form.first_name.data, last_name=form.last_name.data, password=hashedPass,
                          std_id=form.std_id.data, advisor_email=advisor_email)

        db.session.add(newUser)
        db.session.commit()

        flash("Signed Up Successfully!!")
        return redirect(url_for('stdLogin'))

    links = {'Login': 'stdLogin', 'Signup': 'stdSignup'}
    return render_template('formPage.html', form=form, links=links, Name='Sign Up')


@app.route('/stdLogin', methods=['GET', 'POST'])
def stdLogin():
    if current_user.is_authenticated:
        if current_user.type_ == 'student':
            return redirect('/student')
        elif current_user.type_ == 'advisor':
            return redirect('/advisor')

    form = LoginForm(Student)
    if form.validate_on_submit():
        user = Student.query.filter_by(email=form.email.data.lower()).first()

        # if not user.is_confirmed:
        #     return '<h1 style= "text-align: center">Your Email hasn\'t been confirmed yet,' \
        #            '\nPlease <a href="{}">click here</a> to confirm your email <h1>' \
        #         .format(url_for('send_confirmation', email=user.email, _external=True))

        login_user(user, remember=form.remember.data)
        return redirect('/student')

    links = {'Login': 'stdLogin', 'Signup': 'stdSignup'}
    return render_template('formPage.html', form=form, links=links, Name="Login")


@app.route('/advSignup', methods=['GET', 'POST'])
def advSignup():
    if current_user.is_authenticated:
        if current_user.type_ == 'student':
            return redirect('/student')
        elif current_user.type_ == 'advisor':
            return redirect('/advisor')

    form = AdvRegisterForm()

    if form.validate_on_submit():
        password = form.password.data
        hashedPass = generate_password_hash(password, method='sha256')

        newUser = Advisor(first_name=form.first_name.data, last_name=form.last_name.data, password=hashedPass,
                          email=form.email.data.lower())

        db.session.add(newUser)
        db.session.commit()

        flash("Signed Up Successfully!!")
        return redirect(url_for('advLogin'))

    links = {'Login': 'advLogin', 'Signup': 'advSignup'}
    return render_template('formPage.html', form=form, links=links, Name='Sign Up')


@app.route('/advLogin', methods=['GET', 'POST'])
def advLogin():
    if current_user.is_authenticated:
        if current_user.type_ == 'student':
            return redirect('/student')
        elif current_user.type_ == 'advisor':
            return redirect('/advisor')

    form = LoginForm(Advisor)
    if form.validate_on_submit():
        user = Advisor.query.filter_by(email=form.email.data.lower()).first()

        # if not user.is_confirmed:
        #     return '<h1 style= "text-align: center">Your Email hasn\'t been confirmed yet,' \
        #            '\nPlease <a href="{}">click here</a> to confirm your email <h1>' \
        #         .format(url_for('send_confirmation', email=user.email, _external=True))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('advisor'))

    links = {'Login': 'advLogin', 'Signup': 'advSignup'}
    return render_template('formPage.html', form=form, links=links, Name='Log in')


@app.route('/student')
@login_required
def student():
    if current_user.type_ != 'student':
        return redirect('/advisor')

    name = current_user.first_name + ' ' + current_user.last_name
    email = str(current_user.std_id) + '@upm.edu.sa'
    application = current_user.application

    return render_template('student-dashboard.html', name=name, email=email, application=application)


@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if current_user.type_ != 'student':
        return redirect('/advisor')

    form = ApplicationForm()

    application = current_user.application
    if application and not application.pending:
        return abort(403)

    if form.validate_on_submit():
        department = form.department.data
        level = form.level.data
        credits = form.credits.data

        if application is not None:
            application.department = department
            application.level = level
            application.credits = credits

            db.session.commit()
            return redirect('/student')

        student_name = current_user.first_name + ' ' + current_user.last_name
        application = Application(student_id=current_user.std_id, student_name=student_name, level=level,
                                  department=department, credits=credits, advisor_email=current_user.advisor_email)
        db.session.add(application)
        db.session.commit()
        return redirect('/student')

    if application is not None:
        form.department.data = application.department
        form.level.data = application.level
        form.credits.data = application.credits

    return render_template('formPage.html', form=form, Name='Apply')


@app.route('/advisor')
@login_required
def advisor():
    if current_user.type_ != 'advisor':
        return redirect('/student')

    applications = Application.query.filter_by(advisor_email=current_user.email, pending=True).all()

    apps_num = len(applications)
    name = current_user.first_name + " " + current_user.last_name
    email = current_user.email

    return render_template('admin-dashboard.html', name=name, email=email, apps_num=apps_num, applications=applications)


@app.route('/viewApplication/<student_id>', methods=['GET', 'POST'])
@login_required
def viewApplication(student_id):
    if current_user.type_ != 'advisor':
        return abort(403)

    application = Application.query.filter_by(student_id=student_id, advisor_email=current_user.email,
                                              pending=True).first()
    if not application:
        return abort(404)

    form = ViewApplicationForm()

    if form.validate_on_submit():
        comment = form.comment.data
        approved = form.approved.data

        application.pending = False
        application.approved = approved
        application.comment = comment
        db.session.commit()

        if approved:
            # TODO:  Send Approval Email with the comment.
            pass
        else:
            # TODO: Send Disapproval Email with the comment.
            pass
        return redirect('/advisor')

    form.student_name.data = application.student_name
    form.level.data = application.level
    form.credits.data = application.credits
    form.department.data = application.department

    return render_template('formPage.html', form=form, Name='Review')


temp_landing_page = f'''<body>
<a href="/stdSignup" style= "text-align: center" > Student Signup </a> <br/>
<a href="/stdLogin"  style= "text-align: center" > Student Login </a> <br/>
<a href="/advSignup" style= "text-align: center" > Advisor Signup </a> <br/>
<a href="/advLogin"  style= "text-align: center" > Advisor Login </a> <br/>
<body/>
'''


@app.route('/')
def landing():
    if current_user.is_authenticated:
        if current_user.type_ == 'student':
            return redirect('/student')
        elif current_user.type_ == 'advisor':
            return redirect('/advisor')

    return temp_landing_page


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('stdLogin'))


if __name__ == '__main__':
    app.run(debug=True)
