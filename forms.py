from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError, Email
from werkzeug.security import check_password_hash
from wtforms_sqlalchemy.fields import QuerySelectField

from sql_models import Student, Advisor


class StdLoginForm(FlaskForm):
    studentID = StringField('Student ID', validators=[InputRequired(), Length(min=4, max=10)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

    def validate_studentID(self, studentID):

        if not str(studentID.data).isnumeric():
            raise ValidationError("Incorrect ID format")

        user = Student.query.filter_by(std_id=studentID.data).first()

        if not user:
            raise ValidationError('incorrect username or password')
        if not check_password_hash(user.password, self.password.data):
            raise ValidationError('incorrect username or password')


def advisorQuery():
    return Advisor.query.all()


class StdRegisterForm(FlaskForm):
    std_id = StringField('Student ID', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80),
                                                     EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm_password', validators=[InputRequired(), Length(min=8, max=80)])
    first_name = StringField('First Name', validators=[InputRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=3, max=20)])

    advisor = QuerySelectField(query_factory=advisorQuery, allow_blank=False, get_label='email')

    def validate_studentID(self, studentID):

        if not str(studentID).isnumeric() or not (7 < len(str(studentID)) < 10):
            raise ValidationError("Incorrect ID format")

        user = Student.query.filter_by(std_id=studentID.data).first()

        if user:
            raise ValidationError('User already exists')


class AdvRegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired(), Length(min=3, max=20)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email', check_deliverability=True),
                                             Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80),
                                                     EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm_password', validators=[InputRequired(), Length(min=8, max=80)])

    def validate_email(self, email):

        if not str(email.data.lower()).endswith('@upm.edu.sa'):
            raise ValidationError("Not a UPM email.")

        user = Advisor.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('email already exists')


class AdvLoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email', check_deliverability=True),
                                             Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

    def validate_email(self, email):

        user = Advisor.query.filter_by(email=email.data.lower()).first()

        if not user:
            raise ValidationError('incorrect email or password')
        if not check_password_hash(user.password, self.password.data):
            raise ValidationError('incorrect username or password')
