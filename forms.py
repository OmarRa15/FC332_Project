from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectField, TextAreaField, FileField, \
    validators
from wtforms.validators import InputRequired, Length, EqualTo, Email
from werkzeug.security import check_password_hash
from wtforms_sqlalchemy.fields import QuerySelectField

from validations import *
from sql_models import Student, Advisor, User


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(min=7, max=50),
                                             Email(message='Invalid email', check_deliverability=True)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

    def __init__(self, modelName):
        super().__init__()
        self.modelName = modelName

    def validate_email(self, email):

        user = self.modelName.query.filter_by(email=email.data.lower()).first()

        if not user:
            raise ValidationError('incorrect username or password')
        if not check_password_hash(user.password, self.password.data):
            raise ValidationError('incorrect username or password')


def advisorQuery():
    return Advisor.query.all()


class StdRegisterForm(FlaskForm):
    std_id = StringField('Student ID', validators=[InputRequired(), Length(min=7, max=8)])
    first_name = StringField('First Name', validators=[InputRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=3, max=20)])

    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80),
                                                     EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm_password', validators=[InputRequired(), Length(min=8, max=80)])

    advisor = QuerySelectField(query_factory=advisorQuery, allow_blank=False, get_label='email')

    image = FileField('Image File')

    def validate_std_id(self, studentID):
        studentID_validation(studentID.data)

        user = Student.query.filter_by(email=studentID.data + '@upm.edu.sa').first()
        if user:
            raise ValidationError('User already exists')

    def validate_first_name(self, first_name):
        name_validation(first_name.data)

    def validate_last_name(self, lastname):
        name_validation(lastname.data)

    def validate_password(self, password):
        password_validation(password.data)


class AdvRegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email', check_deliverability=True),
                                             Length(max=50)])

    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80),
                                                     EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm_password', validators=[InputRequired(), Length(min=8, max=80)])

    def validate_email(self, email):
        advisorEmail_validations(email.data)

        user = Advisor.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('email already exists')

    def validate_first_name(self, first_name):
        name_validation(first_name.data)

    def validate_last_name(self, lastname):
        name_validation(lastname.data)

    def validate_password(self, password):
        password_validation(password.data)


class ApplicationForm(FlaskForm):
    departments = ['Cyber Security']
    level = IntegerField('Level', validators=[InputRequired()])
    credits = IntegerField('Credits', validators=[InputRequired()])
    department = SelectField('Department', choices=departments, validators=[InputRequired()])
    training_company = StringField('training_company', validators=[InputRequired(), Length(min=5, max=50)])
    description = TextAreaField('description:', validators=[InputRequired(), Length(max=500)])

    def validate_level(self, level):
        level_validation(level.data)

    def validate_credits(self, credits):
        credits_validations(credits.data)


class ViewApplicationForm(FlaskForm):
    student_name = StringField('Student Name', render_kw={'readonly': True})
    level = StringField('Level', render_kw={'readonly': True})
    credits = StringField('Credits', render_kw={'readonly': True})
    department = StringField('Department', render_kw={'readonly': True})
    training_company = StringField('training_company', render_kw={'readonly': True})
    description = TextAreaField('description:', render_kw={'readonly': True})

    comment = TextAreaField('Your Comment:', validators=[InputRequired(), Length(max=500)])
    approved = BooleanField('Approve')


class EmailForm(FlaskForm):
    email = StringField('Enter Your email',
                        validators=[InputRequired(), Email(message='Invalid email', check_deliverability=True),
                                    Length(max=50)])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()

        if not user:
            raise ValidationError("email doesn't exists")


class ResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[InputRequired(), Length(min=8, max=80),
                                                         EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm password', validators=[InputRequired(), Length(min=8, max=80)])

    def validate_password(self, password):
        password_validation(password.data)
