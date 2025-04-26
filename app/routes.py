from app import app
from flask import render_template, redirect, url_for, flash, request, session

# Introductory / Landing Page
@app.route("/")
def home():
    return render_template("home.html")

# Sign Up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Check for existing account
        if existed_account(username):
            flash("Account already existed. Please log in.", "error")
            return redirect(url_for("signup.html"))
        
        # Create user
        create_user(username, password)
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# Log In
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check user credentials and log in
        username = request.form["username"]
        password = request.form["password"]
        if not validate_account(username, password):
            flash("Incorrect login credentials. Please check your username and password", "error")
            return redirect(url_for("login.html"))
    
        session["username"] = username
        return redirect(url_for("wardrobe.html"))

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
