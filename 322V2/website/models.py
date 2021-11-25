from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(400), unique=True)
    password = db.Column(db.String(400))
    first_name = db.Column(db.String(400))
    usertype = db.Column(db.String(400))
    courses = db.relationship('Courses')

class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400))
    course_id = db.Column(db.String(400)) 
    instructor = db.Column(db.String(400)) 
    semester = db.Column(db.String(400)) 
    user = db.Column(db.Integer(), db.ForeignKey('user.id'))

# added Applications, will have a relationship with User and 
#   students enter their name, and GPA -> Float 
#   Instructor enters their subject of interest and their name 
class Applications(db.Model):
    __tablename__ = 'apps'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer) 
    subject_instructor = db.Column(db.String(400))
    gpa_student = db.Column(db.Float)
    name = db.Column(db.String(400))
    type = db.Column(db.String(400))


