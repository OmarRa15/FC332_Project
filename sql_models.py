from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def db_init(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    password = db.Column(db.String(255))
    is_confirmed = db.Column(db.Boolean, default=False)

    image = db.relationship('Image', backref='users', uselist=False)

    type_ = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_on': type_,
        'polymorphic_identity': 'user'
    }


class Administrator(User):
    __tablename__ = "administrator"

    __mapper_args__ = {
        'polymorphic_identity': 'administrator'
    }

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_confirmed = True

    def __repr__(self):
        return str(self.email)


class Advisor(User):
    __tablename__ = "advisor"

    __mapper_args__ = {
        'polymorphic_identity': 'advisor'
    }

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_confirmed = True

    def __repr__(self):
        return str(self.email)


class Student(User):
    __tablename__ = "student"

    advisor_email = db.Column(db.String, db.ForeignKey(Advisor.email))
    application = db.relationship('Application', backref='student', uselist=False)
    advisor = db.relationship(Advisor, backref='student', remote_side=Advisor.email)
    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

    def __init__(self, first_name, last_name, email, password, advisor_email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.advisor_email = advisor_email
        self.is_confirmed = False

    def __repr__(self):
        return 'StdID: ' + str(self.email[:-11]) + ' ' + self.first_name + ' ' + self.last_name + ' ' + str(
            self.advisor_email)


class Image(db.Model):
    __tablename__ = "image"

    user_email = db.Column(db.String, db.ForeignKey(User.email), unique=True, primary_key=True)
    img_data = db.Column(db.LargeBinary, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(255), nullable=False)

    def __init__(self, email, img_data, name, mime_type):
        self.user_email = email
        self.img_data = img_data
        self.name = name
        self.mime_type = mime_type


class Application(db.Model):
    __tablename__ = "application"

    student_email = db.Column(db.String, db.ForeignKey(Student.email), unique=True, primary_key=True)
    student_name = db.Column(db.String(50))
    level = db.Column(db.SmallInteger)
    credits = db.Column(db.Integer)
    department = db.Column(db.String(50))
    training_company = db.Column(db.String(50))
    description = db.Column(db.String(500))
    advisor_email = db.Column(db.String(50))
    comment = db.Column(db.String(500))
    pending = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)

    def __init__(self, student_email, student_name, level, credits, department, training_company, description,
                 advisor_email, comment='', approved=False, pending=True):
        self.student_email = student_email
        self.student_name = student_name
        self.level = level
        self.credits = credits
        self.department = department
        self.training_company = training_company
        self.description = description
        self.advisor_email = advisor_email
        self.comment = comment
        self.pending = pending
        self.approved = approved

    def __repr__(self):
        return 'StdID: ' + str(self.student_email[:-11]) + ' Advisor:' + str(self.advisor_email)
