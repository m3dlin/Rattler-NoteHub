from flask import Flask, render_template, session, request, redirect, url_for, flash
from utils.database import get_course_nums, check_credentials, get_student_info
from dotenv import load_dotenv
import os
app = Flask(__name__)

load_dotenv()
# used for sign in sessions
app.secret_key = os.getenv('SECRET_KEY')

courses_data = {
  "CS1310": "Programming I",
  "TH1301": "Introduction to Theology",
  "CS3300": "Python for Data Analytics",
  "CS3330": "Computer Networks",
  "TH3350": "Moral Theology"
}

# Sample note data (replace with your actual note data)
note_data = {
    "title": "Sample Note",
    "date": "2024-02-05",
    "tags": ["Tag1", "Tag2"],
    "description": "This is a sample note description.",
    "content": "This is the content of the sample note.",
    "visibility": "Public."
}

#########################
# AUTHENTICATION ROUTES #
#########################

# Function to get the number of notes for a given course (replace with your actual logic)
# move this to database.py later on...
def get_notes_count(course_number):
    # Example: Return a placeholder value
    return 2

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

@app.route("/signup")
def sign_up_page():
    return render_template('sign-up-page.html'), 200


@app.route("/addcourses")
def add_courses_page():
    courses = get_course_nums()
    return render_template('add-courses-page.html', courses=courses), 200

@app.route("/home", endpoint='home')
def home_page():
    if 'email' in session:
        student, courses = get_student_info(email=session['email'])
        return render_template('home-page.html', student=student, courses=courses_data), 200
    return 'You are not logged in', 404


@app.route("/guidelines")
def guidelines_page():
    return render_template('guidelines-page.html'), 200

@app.route("/addnote")
def add_note_page():
    return render_template('add-note-page.html'), 200

@app.route("/<courseId>")
def course_page(courseId):
    return render_template('course-page.html', courses=courses_data, course_number=courseId,note_count=get_notes_count(courseId)), 200


#future work: route should be /viewnote<noteId>
@app.route("/viewnote")
def view_note():
    return render_template('note-page.html', note_title=note_data["title"], note_date=note_data["date"],
                           note_tags=note_data["tags"], note_description=note_data["description"],
                           note_content=note_data["content"], note_visibility=note_data["visibility"]), 200


#future work: route should be /editnote<noteId>
@app.route("/editnote")
def edit_note():
    return render_template('edit-note-page.html'),200



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)