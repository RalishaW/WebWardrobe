from app import app
from flask import render_template, redirect, url_for, request, session

# Introductory / Landing Page
@app.route("/")
def home():
    return render_template("home.html")

# Sign Up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # handle form submission
        return redirect(url_for("login"))
    return render_template("signup.html")

# Log In
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check user credentials and log in
        return redirect(url_for("wardrobe"))
    return render_template("login.html")

# Core Pages
@app.route('/wardrobe')
def wardrobe():
    return render_template('wardrobe.html')

@app.route('/outfits')
def outfits():
    return render_template('outfit.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/social')
def social():
    return render_template('social.html')
