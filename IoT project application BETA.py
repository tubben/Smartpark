# IoT project application BETA

from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.route("/monitoring")
def monitoring():
    tempe = random.randint(0, 100)
    return render_template("monitoring.html", temp=tempe)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/")
def standard():
    return render_template("home.html")

@app.route('/post',methods = ["POST"])
def post():
    global besked
    print(request.data)
    besked = request.data
    return ''

@app.route('/postet')
def postet():
    
    return besked


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=False)