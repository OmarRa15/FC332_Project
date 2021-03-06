from flask import Flask, abort, request, Response
from os import environ
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature
import re
from send_mail import send_reset_mail, send_confirmation_mail
from sql_models import db, db_init, User, Student, Advisor, Application, Administrator, Image
from forms import StdRegisterForm, AdvRegisterForm, ApplicationForm, ViewApplicationForm, LoginForm, EmailForm, \
    ResetForm

app = Flask(__name__)

app.config['SECRET_KEY'] = environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL'][0:8] + 'ql' + environ['DATABASE_URL'][8:]
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

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
        return redirect('/' + current_user.type_)

    form = StdRegisterForm()

    if form.validate_on_submit():
        password = form.password.data
        hashedPass = generate_password_hash(password, method='sha256')
        advisor_email = str(form.advisor.data).lower()

        newUser = Student(first_name=form.first_name.data, last_name=form.last_name.data, password=hashedPass,
                          email=form.std_id.data + '@upm.edu.sa', advisor_email=advisor_email)
        db.session.add(newUser)

        image = request.files[form.image.name]

        if image:

            regex = re.match('^[^\'" *;/]+\.((jpg)|(jpeg)|(png))$', image.filename)
            if regex:
                image_name = secure_filename(str(image.filename))

                mime_type = image.mimetype

                image = Image(newUser.email, image.read(), image_name, mime_type)

                db.session.add(image)

        db.session.commit()

        flash("Signed Up Successfully!!")
        return redirect(url_for('stdLogin'))

    links = {'Login': 'stdLogin', 'Signup': 'stdSignup'}
    return render_template('formPage.html', form=form, links=links, Name='Sign Up')


@app.route('/stdLogin', methods=['GET', 'POST'])
def stdLogin():
    if current_user.is_authenticated:
        return redirect('/' + current_user.type_)

    form = LoginForm(Student)
    if form.validate_on_submit():
        user = Student.query.filter_by(email=form.email.data.lower()).first()

        if not user.is_confirmed:
            return '<h1 style= "text-align: center">Your Email hasn\'t been confirmed yet,' \
                   '\nPlease <a href="{}">click here</a> to confirm your email <h1>' \
                .format(url_for('send_confirmation', email=user.email, _external=True))

        login_user(user, remember=form.remember.data)
        return redirect('/student')

    links = {'Login': 'stdLogin', 'Signup': 'stdSignup'}
    return render_template('formPage.html', form=form, links=links, Name="Login")


@app.route('/advLogin', methods=['GET', 'POST'])
def advLogin():
    if current_user.is_authenticated:
        return redirect('/' + current_user.type_)

    form = LoginForm(Advisor)
    if form.validate_on_submit():
        user = Advisor.query.filter_by(email=form.email.data.lower()).first()

        if not user.is_confirmed:
            return '<h1 style= "text-align: center">Your Email hasn\'t been confirmed yet,' \
                   '\nPlease <a href="{}">click here</a> to confirm your email <h1>' \
                .format(url_for('send_confirmation', email=user.email, _external=True))

        login_user(user, remember=form.remember.data)
        return redirect(url_for('advisor'))

    return render_template('formPage.html', form=form, Name='Login')


serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if current_user.is_authenticated:
        return abort(403)

    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(email)
            link = url_for('resetPass', token=token, _external=True)
            if send_reset_mail(recipient=email, link=link):
                message = "Reset email has been sent successfully,\n Please check your email"
                return render_template('messagePage.html', message=message)
            message = "The email could not be sent. Please try again later"
            return render_template('messagePage.html', message=message)

    return render_template('formPage.html', form=form, Name='Enter your email')


@app.route('/resetPass/<token>', methods=['GET', 'POST'])
def resetPass(token):
    if current_user.is_authenticated:
        return abort(403)
    try:
        form = ResetForm()
        email = serializer.loads(token, max_age=1800)
        user = User.query.filter_by(email=email).first()
        if form.validate_on_submit():
            hashedPass = generate_password_hash(form.password.data, method='sha256')
            user.password = hashedPass
            db.session.commit()
            flash("Password has been reset Successfully!!")
            return redirect('/')
        return render_template('formPage.html', form=form, Name='Reset')
    except SignatureExpired:
        return render_template('messagePage.html', message="Signature Expired")
    except BadTimeSignature:
        return abort(404)
    except BadSignature:
        return abort(404)


@app.route('/send_confirmation/<email>')
def send_confirmation(email):
    if current_user.is_authenticated:
        return abort(403)

    user = User.query.filter_by(email=email).first()
    if not user:
        return abort(404)
    if user.is_confirmed:
        return abort(403)

    token = serializer.dumps(email)
    link = url_for('confirm_email', token=token, _external=True)
    if send_confirmation_mail(recipient=email, link=link):
        message = "Email confirmation has been sent successfully, Please check your email\n"
        return render_template('messagePage.html', message=message)

    message = "The email could not be sent. Please try again later"
    return render_template('messagePage.html', message=message)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, max_age=1800)
        user = User.query.filter_by(email=email).first()
        user.is_confirmed = True
        db.session.commit()
        message = "Your email has been confirmed successfully. You can sign in now."
        return render_template('messagePage.html', message=message)
    except SignatureExpired:
        return render_template('messagePage.html', message='Signature Expired')
    except BadTimeSignature:
        return abort(404)
    except BadSignature:
        return abort(404)


@app.route('/student')
@login_required
def student():
    if current_user.type_ != 'student':
        return abort(403)

    name = current_user.first_name + ' ' + current_user.last_name
    email = str(current_user.email)
    application = current_user.application

    return render_template('student-dashboard.html', image=current_user.image, name=name, email=email,
                           application=application)


@app.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if current_user.type_ != 'student':
        return abort(403)

    form = ApplicationForm()

    application = current_user.application
    if application and application.approved:  # application has been approved
        abort(403)

    elif application and not application.pending:  # application has been denied => delete it and start a new one
        db.session.delete(application)
        db.session.commit()
        application = None

    if form.validate_on_submit():
        department = form.department.data
        level = form.level.data
        credits = form.credits.data
        company = form.training_company.data
        description = form.description.data

        if application is not None:
            application.department = department
            application.level = level
            application.credits = credits
            application.training_company = company
            application.description = description

            db.session.commit()
            return redirect('/student')

        student_name = current_user.first_name + ' ' + current_user.last_name
        application = Application(current_user.email, student_name, level, credits, department, company, description,
                                  current_user.advisor_email)
        db.session.add(application)
        db.session.commit()
        return redirect('/student')

    if application is not None:
        form.department.data = application.department
        form.level.data = application.level
        form.credits.data = application.credits
        form.training_company.data = application.training_company
        form.description.data = application.description

    return render_template('formPage.html', form=form, Name='Apply')


@app.route('/advisor')
@login_required
def advisor():
    if current_user.type_ != 'advisor':
        return abort(403)

    applications = Application.query.filter_by(advisor_email=current_user.email, pending=True).all()

    apps_num = len(applications)
    name = current_user.first_name + " " + current_user.last_name
    email = current_user.email

    return render_template('advisor-dashboard.html', name=name, email=email, apps_num=apps_num,
                           applications=applications)


@app.route('/viewApplication/<student_email>', methods=['GET', 'POST'])
@login_required
def viewApplication(student_email):
    if current_user.type_ != 'advisor':
        return abort(403)

    application = Application.query.filter_by(student_email=student_email, advisor_email=current_user.email,
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

        return redirect('/advisor')

    form.student_name.data = application.student_name
    form.level.data = application.level
    form.credits.data = application.credits
    form.department.data = application.department
    form.training_company.data = application.training_company
    form.description.data = application.description

    return render_template('formPage.html', form=form, Name='Review')


@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    if current_user.is_authenticated:
        return redirect('/' + current_user.type_)
    form = LoginForm(Administrator)
    if form.validate_on_submit():
        user = Administrator.query.filter_by(email=form.email.data.lower()).first()
        login_user(user, remember=form.remember.data)

        return redirect(url_for('administrator'))

    return render_template('formPage.html', form=form, Name='Log in')


@app.route('/searchAdvisor')
@login_required
def searchAdvisor():
    if current_user.type_ != 'student':
        return abort(403)

    args = request.args
    advisor_name = args.get('name', default='')

    # A vulnerable Query:
    result = db.session.execute(
        f"SELECT first_name, last_name, email FROM users WHERE type_='advisor' AND first_name='{advisor_name}';").all()

    return render_template('search-Result.html', result=result)


@app.route('/searchStudent')
@login_required
def searchStudent():
    if current_user.type_ != 'advisor':
        return abort(403)

    args = request.args
    student_name = args.get('name', default='')

    result = db.session.execute(
        f"SELECT * FROM student_view WHERE first_name= :name;", {'name': student_name}).all()

    return render_template('search-Result.html', result=result)


@app.route('/administrator')
@login_required
def administrator():
    if current_user.type_ != 'administrator':
        return abort(403)

    studentsNum = len(Student.query.all())
    advisorsNum = len(Advisor.query.all())

    name = current_user.first_name + " " + current_user.last_name
    email = current_user.email

    return render_template('admin-dashboard.html', name=name, email=email, studentNum=studentsNum,
                           advisorNum=advisorsNum)


@app.route('/addAdvisor', methods=['GET', 'POST'])
@login_required
def addAdvisor():
    if current_user.type_ != 'administrator':
        return abort(403)

    form = AdvRegisterForm()

    if form.validate_on_submit():
        password = form.password.data
        hashedPass = generate_password_hash(password, method='sha256')

        db.session.execute(
            f"CALL addAdvisor('{form.first_name.data}','{form.last_name.data}','{hashedPass}','{form.email.data}');")
        db.session.commit()

        return redirect(url_for('administrator'))

    return render_template('formPage.html', form=form, Name='Add Advisor')


@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect('/' + current_user.type_)

    return render_template('landing.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))


@app.route('/image/<email>')
@login_required
def profile_pic(email):
    if current_user.email != email:
        return abort(404)

    image = current_user.image

    if not image:
        return abort(404)

    return Response(image.img_data, mimetype=image.mime_type)


if __name__ == '__main__':
    app.run()
