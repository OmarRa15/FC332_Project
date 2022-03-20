from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from app import app

db = SQLAlchemy(app)


class AdvUsers(db.Model, UserMixin):
    __tablename__ = "adv_users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    is_confirmed = db.Column(db.Boolean, default=True)

    students = db.relationship("StdUsers", backref="adv_users")

    def __init__(self, first_name, last_name, email, password, is_confirmed=True):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_confirmed = is_confirmed

    def __repr__(self):
        return 'ID: ' + str(self.id) + ' ' + self.first_name + ' ' + self.last_name


class StdUsers(db.Model, UserMixin):
    __tablename__ = "std_users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    std_id = db.Column(db.Integer, unique=True)
    password = db.Column(db.String(255))
    is_confirmed = db.Column(db.Boolean, default=True)
    advisor_id = db.Column(db.Integer, db.ForeignKey('adv_users.id'))

    application = db.relationship('Applications', backref='StdUsers', uselist=False)

    def __init__(self, first_name, last_name, std_id, password, advisor_id, is_confirmed=True):
        self.first_name = first_name
        self.last_name = last_name
        self.std_id = std_id
        self.password = password
        self.advisor_id = advisor_id
        self.is_confirmed = is_confirmed

    def __repr__(self):
        return 'StdID: ' + str(self.std_id) + ' ' + self.first_name + ' ' + self.last_name


class Applications(db.Model):
    __tablename__ = "applications"

    student_id = db.Column(db.Integer, db.ForeignKey('std_users.std_id'), unique=True, primary_key=True)
    level = db.Column(db.SmallInteger)
    credits = db.Column(db.Integer)
    department = db.Column(db.String(50))
    advisor = db.Column(db.Integer, db.ForeignKey('adv_users.id'))
    comment = db.Column(db.String(500))
    pending = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)

    def __init__(self, student_id, level, credits, department, advisor, comment, pending=True, approved=True):
        self.student_id = student_id
        self.level = level
        self.credits = credits
        self.department = department
        self.advisor = advisor
        self.comment = comment
        self.pending = pending
        self.approved = approved
