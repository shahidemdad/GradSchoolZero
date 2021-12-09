from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc
from .auth import make_student, make_instructor, make_registrar

from .models import User
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/')
def homepage():
    make_student()
    make_instructor()
    make_registrar()

    data = (
        ("CSC 10300", "Introduction to Computing", "3.9"),
        ("CSC 10300", "Introduction to Computing", "2.4"),
    )


    user = User.query.order_by(desc(User.gpa)).first()
    max_gpa = user.gpa
    student = User.query.filter(User.gpa <= max_gpa).order_by( desc(User.gpa)).limit(5).all()
    return render_template("homepage.html", user=current_user,  table_data=data, data=student)
