from app import app
from flask import render_template, redirect, url_for, request, session

# Introductory / Landing Page
@app.route("/")
def home():
    return render_template("home.html")  # renamed intro.html to home.html

# Sign Up Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # TODO: Handle user registration logic
        return redirect(url_for("login"))
    return render_template("signup.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # TODO: Authenticate user and start session
        return redirect(url_for("wardrobe"))
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    # TODO: Clear user session
    return redirect(url_for("home"))

# Wardrobe View – Upload & Filter Items
@app.route("/wardrobe", methods=["GET", "POST"])
def wardrobe():
    if request.method == "POST":
        # TODO: Handle file upload and save item metadata
        pass
    return render_template("wardrobe.html")

# Outfit View – Create & View Saved Outfits
@app.route("/outfits", methods=["GET", "POST"])
def outfits():
    if request.method == "POST":
        # TODO: Create new outfit from selected items
        pass
    return render_template("outfit.html")

# Analysis View – Wardrobe and Style Stats
@app.route("/analysis")
def analysis():
    # TODO: Pull wardrobe stats and return to template
    return render_template("analysis.html")

# Social View – View & Save Shared Outfits
@app.route("/social")
def social():
    # TODO: Retrieve outfits shared with current user
    return render_template("social.html")
