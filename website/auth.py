from flask import Blueprint, render_template, request, flash, redirect, url_for, session 
from .models import User, Courses, Applications, Complaints, Warnings, UserCourse
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import desc
from flask import request
from flask_request_params import bind_request_params

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
##############################
            if check_password_hash(user.password, password):
                if user.usertype == "Student":
                    if user.status == "S":
                        flash("You have been suspended, wait till period ends. Any questions call Registrar.", category="error")
                        return render_template("login.html", user = current_user)
                    else:
                        login_user(user, remember=True)
                        return redirect(url_for("auth.student_management"))
                elif user.usertype == "Instructor":
                    if user.status == "S":
                        flash("You have been suspended, wait till period ends. Any questions call Registrar.", category="error")
                    else:
                        login_user(user, remember=True)
                        return redirect(url_for("auth.instructor_management"))
                elif user.usertype == "Registrar":
                    login_user(user, remember=True)
                    return redirect(url_for("auth.registrar_management"))

##############################
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        # TODO: look up in the market code how to setup a template for each of the buttoms
        # right now both buttons redirect to apply student
        if request.form['submit_button'] == 'student':
            return redirect(url_for('auth.apply_student'))
        elif request.form['submit_button'] == 'instructor':
            return redirect(url_for('auth.apply_instructor'))
        else:
            pass
    else:
        return render_template("apply.html", user=current_user)


@auth.route('/apply-student', methods = ['GET', 'POST'])
def apply_student(): 
    if request.method == 'POST':
        gpa = request.form.get('gpa') 
        name = request.form.get('fullname')
        new_application = Applications(status = 2, gpa_student = gpa, name = name, type = "Student")
        db.session.add(new_application) 
        db.session.commit()
        flash("Application submitted", category="success")
        return render_template("apply-student.html", user = current_user)
    else: 
        return render_template("apply-student.html", user = current_user)


@auth.route('/apply-instructor', methods = ['GET', 'POST'])
def apply_instructor():
    if request.method == 'POST':
        subject = request.form.get('subject')
        name = request.form.get('fullname')
        new_application = Applications(status = 2, department = subject, name = name, type = "Instructor")
        db.session.add(new_application) 
        db.session.commit()
        flash("Application submitted", category="success")
        return render_template('apply-instructor.html', user = current_user)
    else:
        return render_template('apply-instructor.html', user = current_user)

@auth.route('/application-status', methods = ['GET', 'POST'])
def application(): 
    if request.method == 'POST':
        try:
            name = request.form.get("fullname")
            curr = Applications.query.filter_by(name=name).order_by(Applications.status).first()
            if curr:
                if curr.status == 0:
                    flash("Application accepted", category="success")
                    session["var"] = curr.type      # stores the user type by calling the Column of the db
                    return redirect(url_for("auth.sign_up"))
                if curr.status == 1:
                    flash("Application not accepted", category="error")
                if curr.status == 2:
                    flash("Application pending", category="error") 
            return redirect(url_for("auth.application")) 
        except Exception as e:
            flash("No application", category="error")
            return redirect(url_for("auth.application")) 
    else:
        return render_template('application-status.html', user = current_user) 


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        usertype = session.get('var', None)    # this gets 'var' from application() and uses it to get the user type
        gpa = session.get('gpa', None)
        department = session.get('department', None)

        user = User.query.filter_by(email=email).first()
        # checks the requirements that the inputs are
        if user:
            flash('Email already exists.', category='error')
        # elif len(email) < 4:
        #     flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        # elif len(password1) < 7:
        #     flash('Password must be at least 7 characters.', category='error')
        if usertype == 'Student':
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'), usertype=usertype, gpa=gpa, status = "A") #<<<<<<<<<<<<<<<<<<<<<<<<<<
        elif usertype == 'Instructor':
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'), usertype=usertype,
                            department=department, status = "A") #<<<<<<<<<<<<<<<<<<<<<<<<<<
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash('Account created!', category='success')
        if usertype == 'Student':
            return render_template("student-management.html", user = current_user)
        if usertype == 'Instructor':
            return render_template("instructor-management.html", user = current_user)
        # you cannot sign up as a registrar -> to test you can go to /sign-up 
        else:
            return render_template("registrar-management.html", user = current_user)
    return render_template("sign_up.html", user=current_user)


@auth.route('/registrar-make', methods=['GET', 'POST'])
def make_registrar():
    user = User.query.filter_by(email="r@gmail.com").first()
    if user:
        pass
    else:
        new_user = User(email = "r@gmail.com", first_name = "RegistrarT", password = generate_password_hash("1", method='sha256'), usertype = "Registrar")
        db.session.add(new_user)
        db.session.commit()
    return render_template("make-user.html", user = current_user)


@auth.route('/student-make', methods=['GET', 'POST'])
def make_student():
    user = User.query.filter_by(email="s@gmail.com").first()
    if user:
        pass
    else:
        new_user = User(email = "s@gmail.com", first_name = "Student", password = generate_password_hash("1", method='sha256'), usertype = "Student", status = "A'")
        db.session.add(new_user)
        db.session.commit()

        new_user2 = User(email="c@gmail.com", first_name="Carlos Flores",
                        password=generate_password_hash("1", method='sha256'), usertype="Student", gpa = '3.85', status = "A'")
        db.session.add(new_user2)
        db.session.commit()

        new_user3 = User(email="sg@gmail.com", first_name="Steven Granaturov",
                        password=generate_password_hash("1", method='sha256'), usertype="Student", gpa='3.80', status = "A'")
        db.session.add(new_user3)
        db.session.commit()

        new_user4 = User(email="w@gmail.com", first_name="Willie Shi",
                        password=generate_password_hash("1", method='sha256'), usertype="Student", gpa='3.90', status = "A'")
        db.session.add(new_user4)
        db.session.commit()

        new_user5 = User(email="a@gmail.com", first_name="Atiya Mirza",
                        password=generate_password_hash("1", method='sha256'), usertype="Student", gpa='3.75', status = "A'")
        db.session.add(new_user5)
        db.session.commit()

        if request.method == "POST":
            name = request.form.get('name')
            course_id = request.form.get('course_id')
            instructor = request.form.get('instructor')
            semester = request.form.get('semester')
            capacity = request.form.get('capacity')
            new_course = Courses(course_id=course_id, name=name, instructor=instructor, semester=semester,
                                 capacity=capacity)
            db.session.add(new_course)
            db.session.commit()
            return render_template("courses-make.html", user=current_user)
        else:
            return render_template("courses-make.html", user=current_user)
    return render_template("make-user.html", user=current_user)


@auth.route('/instructor-make', methods=['GET', 'POST'])
def make_instructor():
    user = User.query.filter_by(email="i@gmail.com").first()
    if user:
        pass
    else:
        new_user = User(email = "i@gmail.com", first_name = "Instructor", password = generate_password_hash("1", method='sha256'), usertype = "Instructor")
        db.session.add(new_user)
        db.session.commit()
    return render_template("make-user.html", user = current_user)


@auth.route('/courses-make', methods=['GET', 'POST'])
def make_courses():
    course = Courses.query.filter_by(name = "Introduction to Computing").first()
    if course:
        pass
    else:
        new_user = Courses(course_id = "CSC 10300", name = "Introduction to Computing", instructor = "William E. Skeith", instructor_id = 0, capacity= 90, semester="Fall 2021")
        db.session.add(new_user)
        db.session.commit()

        new_user = Courses(course_id="CSC 10400", name="Discrete Mathematical Structures", instructor="Tahereh Jafarikhah", instructor_id = 0, capacity= 30, semester="Fall 2021")
        db.session.add(new_user)
        db.session.commit()


    if request.method == "POST":
        name = request.form.get('name')
        course_id = request.form.get('course_id')
        instructor = request.form.get('instructor')
        user_instructor = User.query.filter_by(first_name = instructor).first()
        user_id = user_instructor.get_id()
        semester = request.form.get('semester')
        capacity = request.form.get('capacity')
        new_course = Courses(course_id=course_id, name=name, instructor=instructor, instructor_id = user_id, semester=semester,
                            capacity=capacity)
        db.session.add(new_course)
        db.session.commit()
        return render_template("courses-make.html", user=current_user)
    else:
        return render_template("courses-make.html", user=current_user)


@auth.route('/search-classes', methods=['GET', 'POST'])
def search_classes():
    headings = ("Course ID", "Course Name", "Instructor", "Number of Students", "Semester")
    searchTextField = request.args.get('searchTextField')
    if searchTextField:
        coursesData = Courses.query.filter_by(course_id=searchTextField).order_by(Courses.course_id).all()
    else:
        coursesData = Courses.query.order_by(Courses.course_id).all()
    if request.method == "POST":
        #if request.form.get("enrollbutton"): DONT TOUCH, WORKS WITHOUT THIS STATEMENT
        id = request.form.get("enrollbutton")
        print(id)
        course = Courses.query.get(id) # got the course
        courseID = course.id
        courseName = course.name
        courseInstructor = course.instructor
        courseSemester = course.semester
        new_usercourse = UserCourse(name=courseName, course_id=courseID, instructor=courseInstructor, semester=courseSemester, grade = "")
        db.session.add(new_usercourse)
        db.session.commit()
        return redirect(url_for('auth.search_classes', user=current_user, table_headings=headings, data=coursesData))

    else:
        return render_template("search-classes.html", user=current_user, table_headings=headings, data=coursesData)

    print(request.method)
    return render_template("search-classes.html", user=current_user, table_headings=headings, data=coursesData)


@auth.route('/cancel-course', methods=['GET', 'POST'])
def cancel_course():
    headings = ("Course ID", "Course Name", "Instructor", "Number of Students", "Semester")
    coursesData = Courses.query.order_by(Courses.course_id).all()
    if request.method == "POST":
        id = request.form.get("cancelbutton")
        course = Courses.query.get(id)
        print(id)
        db.session.delete(course)
        db.session.commit()
        coursesData = Courses.query.order_by(Courses.course_id).all()
        return render_template("course-cancellation.html", user=current_user, table_headings=headings, data=coursesData)
    else:
        return render_template("course-cancellation.html", user=current_user, table_headings=headings, data=coursesData)


@auth.route('/drop-class', methods=['GET', 'POST'])
def drop_classes():
    headings = ("Course ID", "Course Name", "Instructor", "Semester")
    userCourses = UserCourse.query.order_by(UserCourse.course_id).all()
    if request.method == "POST":
        id = request.form.get("dropbutton")
        course = UserCourse.query.get(id)
        print(id)
        db.session.delete(course)
        db.session.commit()
        userCourses = UserCourse.query.order_by(UserCourse.course_id).all()
    return render_template("drop-class.html", user=current_user, table_headings=headings, data=userCourses)


@auth.route('/course-management', methods=['GET', 'POST'])
def course_management():
    return render_template("course-management.html", user=current_user)


@auth.route('/student-view', methods=['GET', 'POST'])
def student_view():
    user = User.query.order_by(desc(User.gpa)).first()
    max_gpa = user.gpa
    student = User.query.filter(User.gpa <= max_gpa).order_by(desc(User.gpa)).limit(5).all()
    return render_template("student-view.html", user=current_user, data=student)


@auth.route('/applications', methods=['GET', 'POST'])
def applications():
    apps = Applications.query.filter_by(status=2).order_by( desc(Applications.type)).all()
    if request.method == 'POST':
        if request.form.get('submit_button'):
            id = request.form.get('submit_button')
            flash(id, category="success")
            change = Applications.query.get(id)
            change.status = 1
            db.session.commit()
            flash("Rejected", category="error")
            apps = Applications.query.filter_by(status=2).order_by( desc(Applications.type)).all()
            return render_template("applications.html", app = apps, user=current_user)

        elif request.form.get('submit_button1'):
            id = request.form.get('submit_button1')
            remove = Applications.query.get(id)
            re = Applications.query.filter_by(id=id).first()
            if re.type == "Instructor":
                session["department"] = re.department
            else:
                session["gpa"] = re.gpa_student
            remove.status = 0
            db.session.commit()
            flash("Accepted", category="success")
            apps = Applications.query.filter_by(status=2).order_by( desc(Applications.type)).all()
            return render_template("applications.html", app = apps, user=current_user)
    else:
        return render_template("applications.html", app = apps, user=current_user)


@auth.route('/warnings', methods=['GET', 'POST'])
def warnings():
    return render_template("warnings.html", user=current_user)


# registrar handles std/instr and instr/std complaints
@auth.route('/complaints', methods=['GET', 'POST'])
def complaints():
    comps = Complaints.query.order_by(Complaints.id).all()
    if request.method == 'POST':
        # if warning complainER
        if request.form.get('complainer_button'):
            _id = request.form.get('complainer_button') 
            complaints = Complaints.query.filter_by(id=_id).all()
            complaint = complaints[0]     
            flash(_id, category="success")
            warn_email = complaint.complainer_email
            if complaint.ctype == "Student":
                new_warning = Warnings(wtype = "Invalid complaint about instructor", email_warned = warn_email, complaint = complaint.complaint)
            elif complaint.ctype == "Instructor":
                new_warning = Warnings(wtype = "Invalid complaint about student", complaint = complaint.complaint, email_warned = warn_email)
            db.session.add(new_warning)
            flash("Warning sent", category="success")
            db.session.delete(complaint)
            db.session.commit()
            comps = Complaints.query.order_by(Complaints.id).all()
            return render_template("complaints.html", comp = comps, user=current_user)
        # if warning complainEE
        elif request.form.get('complainee_button'):
            _id = request.form.get('complainee_button')
            complaints = Complaints.query.filter_by(id=_id).all()
            complaint = complaints[0]
            flash(_id, category="success")
            warn_email = complaint.complainee_email
            if complaint.ctype == "Student":
                new_warning = Warnings(wtype = "Complaint from student", complaint = complaint.complaint, email_warned = warn_email)
            elif complaint.ctype == "Instructor":
                new_warning = Warnings(wtype = "Complaint from instructor", complaint = complaint.complaint, email_warned = warn_email)
            db.session.add(new_warning)
            flash("Warning sent", category="success")
            db.session.delete(complaint)
            db.session.commit()
            comps = Complaints.query.order_by(Complaints.id).all()
            return render_template("complaints.html", comp = comps, user=current_user)
    else:       
        return render_template("complaints.html", comp = comps, user=current_user)


# for the management pages
@auth.route('/student-management', methods=['GET', 'POST'])
def student_management():
    if request.method == 'POST':
        if request.form['submit_button'] == 'class-overview':
            return redirect(url_for('auth.class_overview'))
        elif request.form['submit_button'] == 'search-classes':
            return redirect(url_for('auth.search_classes'))
        elif request.form['submit_button'] == 'drop-classes':
            return redirect(url_for('auth.drop_classes'))
        elif request.form['submit_button'] == 'student-instructor-complaint':
            return redirect(url_for('auth.student_instructor_complaint'))
        elif request.form['submit_button'] == 'student-student-complaint':
            return redirect(url_for('auth.student_student_complaint'))
        elif request.form['submit_button'] == 'student-warnings':
            return redirect(url_for('auth.student_warnings'))
        elif request.form['submit_button'] == 'records':
            return redirect(url_for('auth.records'))
        else:
            return render_template("student-management.html", user=current_user)
    else:
        return render_template("student-management.html", user=current_user)
    
@auth.route('/class-overview', methods=['GET', 'POST'])
def class_overview():
    if request.method == 'POST':
        pass
    else:
        userCourses = UserCourse.query.order_by(UserCourse.course_id).all()
        headings = ("Course ID", "Course Name", "Instructor", "Semester")
        return render_template("class-overview.html", user=current_user, table_headings=headings, data=userCourses)
    
# student complaints about instructor to registrar
@auth.route('/student-instructor-complaint', methods=['GET', 'POST'])
def student_instructor_complaint():
    if request.method == 'POST':
        fname = request.form.get('firstName')
        email1 = request.form.get('email1')
        email2 = request.form.get('email2')
        complaint = request.form.get('complaint')
        new_complaint = Complaints(fname = fname, ctype = "Student", complainer_email = email1, complainee_email = email2, complaint = complaint)
        db.session.add(new_complaint)
        db.session.commit()
        flash("Complaint submitted", category="success")
        return render_template("student-instructor-complaint.html", user=current_user)
    else:
        return render_template("student-instructor-complaint.html", user=current_user)
    
# student views warnings from registrar
@auth.route('/student-warnings', methods=['GET', 'POST'])
def student_warnings():
    warnings = Warnings.query.filter_by(email_warned=current_user.email).all()
    return render_template("student-warnings.html", user=current_user, warnings=warnings)   
    
@auth.route('/records', methods=['GET', 'POST'])
def records():
    if request.method == 'POST':
        pass
    else:
        userCourses = UserCourse.query.order_by(UserCourse.course_id).all()
        headings = ("Course ID", "Course Name", "Instructor", "Semester", "Grade")
        return render_template("records.html", user=current_user, table_headings=headings, data=userCourses)


@auth.route('/instructor-management', methods=['GET', 'POST'])
def instructor_management():
    if request.method == 'POST':
        if request.form['submit_button'] == 'grade-students':
            return redirect(url_for('auth.grade_students'))
        elif request.form['submit_button'] == 'my-courses':
            return redirect(url_for('auth.my_courses'))
        elif request.form['submit_button'] == 'student-records':
            return redirect(url_for('auth.student_view'))
        elif request.form['submit_button'] == 'instructor-student-complaint':
            return redirect(url_for('auth.instructor_student_complaint'))
        elif request.form['submit_button'] == 'instructor-warnings':
            return redirect(url_for('auth.instructor_warnings'))
        else:
            return render_template("instructor-management.html", user=current_user)
    else:
        return render_template("instructor-management.html", user=current_user)


@auth.route('/grade-students', methods=['GET', 'POST'])
def grade_students():
    headings = ("Student ID", "Student Name", "Course Name", "Grade")
    user_id  =current_user.get_id()
    course = Courses.query.filter_by(instructor=current_user.getFName()).first()
    list_users = UserCourse.query.filter_by(course_id=course.id).all() # Returns UserCourse Object List
    listOfStudents = []
    listOfStudentID = []
    for student in list_users:
        # Get pkeys
        studentID = student.id
        listOfStudentID.append(studentID)
        nameOfUser = User.query.filter_by(id=studentID).first()
        studentName = nameOfUser.first_name
        listOfStudents.append(studentName)
    nameList = []
    gradeList = []
    for data in list_users:
        courseName = data.name
        courseGrade = data.grade
        nameList.append(courseName)
        gradeList.append(courseGrade)
    if request.method == "POST":
        id = request.form.get("grade_button")
        temp = UserCourse.query.get(id)
        temp.grade = request.form.get("grade")
        db.session.commit()
        return render_template("grade-students.html", user=current_user, table_headings=headings, data=listOfStudents, data2=nameList, data3=gradeList, length = len(listOfStudents), data4=listOfStudentID)
    else:
        return render_template("grade-students.html", user=current_user, table_headings=headings,data=listOfStudents, data2=nameList, data3=gradeList, length = len(listOfStudents), data4=listOfStudentID)
    return render_template("grade-students.html", user=current_user, table_headings=headings, data=listOfStudents, data2=nameList, data3=gradeList, length = len(listOfStudents), data4=listOfStudentID)


@auth.route('/my-courses', methods=['GET', 'POST'])
def my_courses():
    headings = ("Course ID", "Course Name", "Semester", "Capacity")
    coursesdata = Courses.query.filter_by(instructor=current_user.getFName()).all()
    if request.method == 'POST':
        return render_template("my-courses.html", user=current_user, table_headings=headings, data=coursesdata)
    else:
        return render_template("my-courses.html", user=current_user, table_headings=headings, data=coursesdata)


@auth.route('/student-records', methods=['GET', 'POST'])
def student_records():
    if request.method == 'POST':
        pass
    else:
        userCourses = UserCourse.query.order_by(UserCourse.course_id).all()
        headings = ("Course ID", "Course Name", "Instructor", "Semester", "Grade")
        return render_template("student-records.html", user=current_user, table_headings=headings, data=userCourses)
    
# instructor complaints about student to registrar  
@auth.route('/instructor-student-complaint', methods=['GET', 'POST'])
def instructor_student_complaint():
    if request.method == 'POST':
        fname = request.form.get('firstName')
        email1 = request.form.get('email1')
        email2 = request.form.get('email2')
        complaint = request.form.get('complaint')
        new_complaint = Complaints(fname = fname, ctype = "Instructor", complainer_email = email1, complainee_email = email2, complaint = complaint)
        db.session.add(new_complaint)
        db.session.commit()
        flash("Complaint submitted", category="success")
        return render_template("instructor-student-complaint.html", user=current_user)
    else:
        return render_template("instructor-student-complaint.html", user=current_user)
    
# instructor views warnings from registrar  
@auth.route('/instructor-warnings', methods=['GET', 'POST'])
def instructor_warnings():
    warnings = Warnings.query.filter_by(email_warned=current_user.email).all()
    return render_template("instructor-warnings.html", user=current_user, warnings=warnings)  

@auth.route('/registrar-management', methods=['GET', 'POST'])
def registrar_management():
    if request.method == 'POST':
        if request.form['submit_button'] == 'evaluate-instructor':
            return redirect(url_for('auth.evaluate_instructor'))
        elif request.form['submit_button'] == 'cancel-course':
            return redirect(url_for('auth.cancel_course'))
        elif request.form['submit_button'] == 'student-suspension':
            return redirect(url_for('auth.student_suspension'))
        elif request.form['submit_button'] == 'instructor-suspension':
            return redirect(url_for('auth.instructor_suspension'))
        elif request.form['submit_button'] == 'student-termination':
            return redirect(url_for('auth.student_termination'))
        elif request.form['submit_button'] == 'class-ratings':
            return redirect(url_for('auth.class_ratings'))
        else:
            return render_template("registrar-management.html", user=current_user)
    else:
        return render_template("registrar-management.html", user=current_user)

@auth.route('/evaluate-instructor', methods=['GET', 'POST'])
def evaluate_instructor():
    headings = ("ID", "Instructor Name", "Email")
    user = User.query.filter_by(usertype="Instructor").order_by(User.first_name).all()
    if request.method == 'POST':
        if request.form.get("warn_button"):
            id = request.form.get("warn_button")
            #suspend = User.query.get(id)
            #suspend.status = "S"
            #db.session.commit()
            flash("Warned", category="error")
            user = User.query.filter_by(usertype="Instructor").order_by(User.first_name).all()
            return render_template("evaluate-instructor.html", data=user, user=current_user, table_headings=headings)
    else:
        return render_template("evaluate-instructor.html", data=user, user=current_user, table_headings=headings)


@auth.route('/student-suspension', methods=['GET', 'POST'])
def student_suspension():
    user = User.query.filter_by(usertype="Student").order_by(User.first_name).all()
    if request.method == 'POST':
        if request.form.get("submit_button"):
            id = request.form.get("submit_button")
            suspend = User.query.get(id)
            suspend.status = "S"
            db.session.commit()
            flash("Suspended", category="error")
            user = User.query.filter_by(usertype="Student").order_by(User.first_name).all()
            return render_template("student-suspension.html", data = user, user=current_user)
        elif request.form.get("submit_button2"):
            id = request.form.get("submit_button2")
            remove = User.query.get(id)
            remove.status = "A"
            db.session.commit()
            flash("Ready", category="success")
            user = User.query.filter_by(usertype="Student").order_by(User.first_name).all()
            return render_template("student-suspension.html", data = user, user=current_user)
    else:
        return render_template("student-suspension.html", data = user, user=current_user)


@auth.route('/instructor-suspension', methods=['GET', 'POST'])
def instructor_suspension():
    user = User.query.filter_by(usertype="Instructor").order_by(User.first_name).all()
    if request.method == 'POST':
        if request.form.get("submit_button"):
            id = request.form.get("submit_button")
            suspend = User.query.get(id)
            suspend.status = "S"
            db.session.commit()
            flash("Suspended", category="error")
            user = User.query.filter_by(usertype="Instructor").order_by(User.first_name).all()
            return render_template("instructor-suspension.html", data = user, user=current_user)
        elif request.form.get("submit_button2"):
            id = request.form.get("submit_button2")
            remove = User.query.get(id)
            remove.status = "A"
            db.session.commit()
            flash("Ready", category="success")
            user = User.query.filter_by(usertype="Instructor").order_by(User.first_name).all()
            return render_template("instructor-suspension.html", data = user, user=current_user)
    else:
        return render_template("instructor-suspension.html", data = user, user=current_user)


@auth.route('/student-termination', methods=['GET', 'POST'])
def student_termination():
    lowgpa = 2
    students = User.query.filter(User.gpa < lowgpa).all()
    print(students)
    if request.method == 'POST':
        _id = request.form.get('expel_button')
        stds = User.query.filter_by(id=_id).all()
        stud = stds[0]
        db.session.delete(stud)
        db.session.commit()
        flash("Student expelled", category="success")
        students = User.query.filter(User.gpa < lowgpa).all()
        return render_template("student-termination.html", student = students, user=current_user)
    else:
        return render_template("student-termination.html", student = students, user=current_user)


@auth.route('/class-ratings', methods=['GET', 'POST'])
def class_ratings():
    if request.method == 'POST':
        pass
    else:
        return render_template("class-ratings.html", user=current_user)