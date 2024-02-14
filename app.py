from flask import Flask, render_template

app = Flask(__name__)


courses = {
  "CS1310": "Programming I",
  "TH1301": "Introduction to Theology",
  "CS3300": "Python for Data Analytics",
  "CS3340": "Computer Networks",
  "TH3350": "Moral Theology"
}



@app.route("/") #empty route, homepage route
def login_page():
    return render_template('login-page.html'), 200


@app.route("/home")
def home_page():
    return render_template('home-page.html', courses=courses), 200


@app.route("/guidelines")
def guidelines_page():
    return render_template('guidelines-page.html'), 200

@app.route("/addnote")
def add_note_page():
    return render_template('add-note-page.html'), 200

@app.route("/course/<courseId>")
def course_page(courseId):
    return render_template('course-page.html', courses=courses, course_number=courseId,note_count=0), 200


#future work: route should be /viewnote/<noteId>
@app.route("/viewnote")
def view_note_page():
    return render_template('note-page.html'),200



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)