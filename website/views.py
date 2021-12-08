from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User
from . import db
import json

views = Blueprint('views', __name__)



@views.route('/')
def homepage():
    data = (
        ("CSC 10300", "Introduction to Computing", "3.9"),
        ("CSC 10300", "Introduction to Computing", "2.4"),
    )

    student = User.query.order_by(User.gpa).all()
    return render_template("homepage.html", user=current_user,  table_data=data, data=student)
