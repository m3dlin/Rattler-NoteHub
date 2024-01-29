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
def index():
    return render_template('index.html',
                           courses=courses), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)