from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from app import app

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    password = db.Column(db.String(255))
    is_confirmed = db.Column(db.Boolean, default=True)

    type_ = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_on': type_,
        'polymorphic_identity': 'user'
    }


class Advisor(User):
    __tablename__ = "advisor"

    email = db.Column(db.String(50), unique=True)

    __mapper_args__ = {
        'polymorphic_identity': 'advisor'
    }

    def __init__(self, first_name, last_name, email, password, is_confirmed=True):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_confirmed = is_confirmed

    def __repr__(self):
        return str(self.email)


class Student(User):
    __tablename__ = "student"

    std_id = db.Column(db.Integer, unique=True)

    advisor_email = db.Column(db.String, db.ForeignKey(Advisor.email))
    application = db.relationship('Application', backref='student', uselist=False)
    advisor = db.relationship(Advisor, backref='student', remote_side=Advisor.email)
    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

    def __init__(self, first_name, last_name, std_id, password, advisor_email, is_confirmed=True):
        self.first_name = first_name
        self.last_name = last_name
        self.std_id = std_id
        self.password = password
        self.advisor_email = advisor_email
        self.is_confirmed = is_confirmed

    def __repr__(self):
        return 'StdID: ' + str(self.std_id) + ' ' + self.first_name + ' ' + self.last_name + str(self.advisor_email)


class Application(db.Model):
    __tablename__ = "application"

    student_id = db.Column(db.Integer, db.ForeignKey(Student.std_id), unique=True, primary_key=True)
    student_name = db.Column(db.String(50))
    level = db.Column(db.SmallInteger)
    credits = db.Column(db.Integer)
    department = db.Column(db.String(50))
    advisor_email = db.Column(db.String(50))
    comment = db.Column(db.String(500))
    pending = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)

    def __init__(self, student_id, student_name, level, credits, department, advisor_email, comment='', approved=False,
                 pending=True):
        self.student_id = student_id
        self.student_name = student_name
        self.level = level
        self.credits = credits
        self.department = department
        self.advisor_email = advisor_email
        self.comment = comment
        self.pending = pending
        self.approved = approved

    def __repr__(self):
        return 'StdID: ' + str(self.student_id) + ' Advisor:' + str(self.advisor_email) + ' Cred' + str(self.credits)
