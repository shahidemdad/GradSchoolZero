from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(400), unique=True)
    password = db.Column(db.String(400))
    first_name = db.Column(db.String(400))
    usertype = db.Column(db.String(400))
    gpa = db.Column(db.Integer)
    department = db.Column(db.String(400))
    status = db.Column(db.String(1))  ####################
    courses = db.relationship('Courses')

    def getFName(self):
        return self.first_name

    def get_id(self):
        return self.id


class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400))
    course_id = db.Column(db.String(400))
    instructor = db.Column(db.String(400))
    instructor_id = db.Column(db.Integer)
    semester = db.Column(db.String(400))
    capacity = db.Column(db.Integer)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    def getID(self):
        return id

# added Applications, will have a relationship with User and
#   students enter their name, and GPA -> Float 
#   Instructor enters their subject of interest and their name 
class Applications(db.Model):
    __tablename__ = 'apps'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)
    department = db.Column(db.String(400))
    gpa_student = db.Column(db.Float)
    name = db.Column(db.String(400))
    type = db.Column(db.String(400))


# complaints to registrar
class Complaints(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(400))
    ctype = db.Column(db.String(400))
    complainer_email = db.Column(db.String(400))
    complainee_email = db.Column(db.String(400))
    complaint = db.Column(db.String(400))

    def __repr__(self):
        return self.complainer_email + " " + self.complainee_email


# warnings to instructor/student
class Warnings(db.Model):
    __tablename__ = 'warnings'
    id = db.Column(db.Integer, primary_key=True)
    wtype = db.Column(db.String(400))
    complaint = db.Column(db.String(400))
    email_warned = db.Column(db.String(400))


class UserCourse(db.Model):
    __tablename__ = 'usercourses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400))
    course_id = db.Column(db.String(400))
    instructor = db.Column(db.String(400))
    grade = db.Column(db.String(10))
    semester = db.Column(db.String(400))
