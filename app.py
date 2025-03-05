"""
This module runs the website's app and contains all the routes for the website
"""

from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
from utils.database import (get_course_nums, check_credentials, get_student_info,get_student_id,
                            get_course_details, get_note, get_note_tags, get_user_notes, 
                            add_courses_to_user, Student, add_student_to_db, check_student_id, 
                            get_bookmarked_notes, get_course_notes, get_note_count, get_list_of_tags,
                            update_selected_note, delete_selected_note, Note, increment_upvotes,
                            increment_downvotes, add_bookmark, delete_bookmark, check_bookmark_status, 
                            add_note_to_db,get_course_notes_with_tags, add_discussion_post, get_discussion_posts,
                            add_comment_to_post, get_comment_from_note, add_comment_to_note, get_notifications)
from utils.firebase import delete_file_from_firebase, upload_to_firebase
from dotenv import load_dotenv
import os
import json
app = Flask(__name__)

load_dotenv()
# used for sign in sessions
app.secret_key = os.getenv('SECRET_KEY')



#########################
# AUTHENTICATION ROUTES #
#########################

# first route when user goes to website.
@app.route("/",endpoint='login')
def login_page():
    return render_template('login-page.html'), 200

@app.route("/login", methods=['POST'])
def login_session():
    if request.method == 'POST':
        # collecting email and password from the name fields in the form (ex: name=email)
        email = request.form['email']
        password = request.form['password']

        # sends the form answers to be verified. If successful, redirect user to the home page
        if check_credentials(email=email,password=password):
            session['email'] = request.form['email']
            return redirect(url_for('home'))
        flash('Invalid email or password. Please try again.', 'error') # else, send a error flash message
    
    if 'email' in session:
        redirect(url_for('home'))
    return redirect("/") # sends user back to the login screen for a new attempt
            
@app.route('/logout')
def logout():
    # remove the user from the session if it's there
    session.pop('email', None)
    return redirect(url_for('login'))

  
@app.route("/signup", endpoint='signup')
def sign_up_page():
    return render_template('sign-up-page.html'), 200

@app.route('/add_user', methods=['POST'])
def add_user():
    # collecting fields from the sign up page
    first_name = request.form['fname']
    last_name = request.form['lname']
    student_id = request.form['StudentID']
    email = request.form['Email'] + "@mail.stmarytx.edu"
    password = request.form['Pword']

    # checks to see if the studentID is already linked to another account, 
    # if so the user will be redirected back to the sign up page.
    if check_student_id(student_id):
        flash("Student ID already has an account.", "error")
        return redirect(url_for('signup'))
    else:
        # created new student object
        new_student = Student(studentId=student_id, firstName=first_name, lastName=last_name, email=email)
        new_student.set_password(password)
        add_student_to_db(new_student)
        flash("Account successfully created!")
        return redirect(url_for('login'))  # redirect to login screen after submission
        
    


#########################
#    MAIN/HOME ROUTES   #
#########################

@app.route("/home", endpoint='home')
def home_page():
    if 'email' in session:
        student, courses = get_student_info(email=session['email'])

        course_details = []

        # Get details of each course for the logged-in student
        for course in courses:
            course_details.append({"id": course["id"], "name": course["name"]})


        notes = get_user_notes(email=session['email'])
        bookmarks = get_bookmarked_notes(email=session['email'])

        return render_template('home-page.html', student=student, courses=course_details, notes=notes, bookmarks=bookmarks), 200
    return 'You are not logged in', 404


@app.route("/guidelines")
def guidelines_page():
    return render_template('guidelines-page.html'), 200



#########################
#       SUB ROUTES      #
#########################

@app.route("/addcourses")
def add_courses_page():
    courses = get_course_nums()
    return render_template('add-courses-page.html', courses=courses), 200


@app.route('/submit_courses', methods=['POST'])
def submit_courses():

    selected_courses_json = request.form.getlist('hiddenCourses') # get the json response from the form from add-courses-page.html

    selected_courses = json.loads(selected_courses_json[0]) # convert the json into a regular list in python
    
    add_courses_to_user(selected_courses, email=session['email'])
    return redirect(url_for('home'))  # redirect to home after submission


# display course page
@app.route("/<courseId>", methods=["GET", "POST"])
def course_page(courseId):
    course_id = courseId
    course_details = get_course_details(course_id)
    course_notes = get_course_notes(course_id)
    discussion_posts = get_discussion_posts(course_id)
    
    if request.method == "POST":
        # if user is searching for tags
        if 'tag' in request.form:
            tag = request.form.get('tag')
            course_notes = get_course_notes_with_tags(courseId=course_id, tag=tag)
        # if user is creating a new discussion post
        elif 'discussionTitle' in request.form and 'discussionMessage' in request.form:
            discussion_title = request.form.get('discussionTitle')
            discussion_message = request.form.get('discussionMessage')
            add_discussion_post(course_id, get_student_id(session['email']),discussion_title, discussion_message)
            return redirect(url_for('course_page', courseId=course_id))
        # if user is creating a new comment on a discussion post
        elif 'discussionPostID' in request.form:
            discussion_post_id = request.form.get('discussionPostID')
            comment_message = request.form.get(f'commentMessage{discussion_post_id}')
            if comment_message:
                add_comment_to_post(discussion_post_id, get_student_id(session['email']), comment_message)
                return redirect(url_for('course_page', courseId=course_id))
    bookmark_status_list = []

    # Check bookmark status for each note
    # this is to check what notes the user has already bookmarked, so the bookmark icon is filled in correctly
    for note in course_notes:
        is_bookmarked = check_bookmark_status(noteId=note.noteId, email=session['email'])
        bookmark_status_list.append(is_bookmarked)

    if course_details:
        return render_template('course-page.html', course_number=course_id, course=course_details, 
                               note_count=get_note_count(course_id), notes=course_notes,
                               bookmark_status_list=bookmark_status_list,tags=get_list_of_tags(), 
                               discussion_posts=discussion_posts), 200
    else:
        return 'Course not found', 404
    

@app.route("/addnote")
def add_note_page():
    tags = get_list_of_tags()
    student, courses = get_student_info(email=session['email'])
    id_values = [course['id'] for course in courses]
    return render_template('add-note-page.html', tags=tags,courses=id_values), 200

@app.route("/submit_note",methods=['POST'])
def submit_note():
    # retreive the updated information from the note
    courseId = request.form.get('courseName')
    title = request.form.get('titlename')
    description = request.form.get('descriptionName')
    studentId = get_student_id(email=session['email'])
    visibility = request.form.get('visibilityName')
    tag = request.form.get('tag')
    pdf_file = request.files['pdf_file']

    if pdf_file:
        # temporarily saving the pdf file
        file_path = f"uploads/{pdf_file.filename}"
        pdf_file.save(file_path)

        uploaded_url = upload_to_firebase(file_path)
        os.remove(file_path) # remove the temp file
        
        if add_note_to_db(courseId,title,description,studentId,visibility,tag, uploaded_url):
            return redirect(url_for('home'))
    else:
        return 'Could not complete adding note', 404



@app.route('/inbox', methods=['GET'])
def inbox_page():

    notifications = get_notifications(get_student_id(session['email']))

    return render_template('inbox-page.html', notifications=notifications), 200


# FUTURE - 'quiz<noteId>' route to be implemented
@app.route('/quiz', methods=['GET'])
def quiz_page():
    return render_template('quiz-page.html'), 200



# future work: ensure that the note is made public
# currently, if anyone has access to the note id, they can view the note
@app.route('/viewnote<noteId>', methods=['GET','POST'])
def view_note(noteId):
    if 'commentMessage' in request.form:
    # if user submits a comment on the note
        comment = request.form.get('commentMessage')
        if comment:
            add_comment_to_note(noteId, get_student_id(session['email']), comment)
            return redirect(url_for('view_note', noteId=noteId ))
    
    note = get_note(noteId)
    tags = get_note_tags(note)
    comments = get_comment_from_note(noteId)
    return render_template('note-page.html',note = note, tags = tags, comments = comments), 200



# future work: ensure that the user who is logged in is the only one who can edit the note
# currently, if anyone has access to the note id, they can edit any note they want.
@app.route("/editnote<noteId>")
def edit_note(noteId):
    note = get_note(noteId)
    tags = get_list_of_tags()
    return render_template('edit-note-page.html', note=note, tags=tags),200

@app.route("/update_note<noteId>", methods=['POST'])
def update_note(noteId):
    # retreive the updated information from the note
    updated_title = request.form.get('title')
    updated_description = request.form.get('description')
    updated_tag = request.form.get('tag')
    updated_visibility = request.form.get('visibility')

    if update_selected_note(noteId=noteId, title=updated_title, description=updated_description,
                            tag=updated_tag, visibility=updated_visibility):
        return redirect(url_for('home'))
    else:
        return 'Could not complete updating note', 404
    



@app.route("/delete_note", methods=['POST'])
def delete_note():
    note_id = int(request.form.get('hiddenNoteId')) # retrieved from the edit page
    note = get_note(noteId=note_id)
    url = note.file_path # file path from the note object used to delete file from firebase

    if delete_selected_note(note_id):
        delete_file_from_firebase(url)
        return redirect(url_for('home'))
    else:
        return 'Could not complete deleting note', 404



@app.route('/upvote', methods=['POST'])
def upvote():
    data = request.get_json()  # noteId is sent in JSON format
    note_id = data.get('noteId')
    # Update the upvotes count in the database
    new_upvotes_count = increment_upvotes(note_id)
    return jsonify({'upvotes': new_upvotes_count})


@app.route('/downvote', methods=['POST'])
def downvote():
    data = request.get_json()  # noteId is sent in JSON format
    note_id = data.get('noteId')
    # Update the downvote count in the database
    new_downvotes_count = increment_downvotes(note_id)
    return jsonify({'downvotes': new_downvotes_count})


@app.route('/bookmark', methods=['POST'])
def bookmark():
    data = request.get_json()  # noteId is sent in JSON format
    note_id = data.get('noteId')
    bookmark_status = data.get('bookmarkStatus')

    if bookmark_status == 'filled':
        if add_bookmark(noteId=note_id, email=session['email']):
            message = 'bookmark added'
        else:
            message = 'added error'

    elif bookmark_status == 'empty':
        if delete_bookmark(noteId=note_id, email=session['email']):
            message = 'bookmark deleted'
        else:
            message = 'delete error'

    else:
        message = 'error'

    return jsonify(message=message), 200






#########################
#        TESTING        #
#########################

@app.route("/test")
def testing():
    notes = get_user_notes(email=session['email'])
    return render_template('test.html', notes = notes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)