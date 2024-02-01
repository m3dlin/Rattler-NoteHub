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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)