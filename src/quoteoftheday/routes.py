import random

from featuremanagement.azuremonitor import track_event
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user
from . import azure_app_config, feature_manager, db, bcrypt
from .model import Quote, Users

bp = Blueprint("pages", __name__)

@bp.route("/", methods=["GET"])
def index():
    global azure_app_config
    # Refresh the configuration from App Configuration service.
    azure_app_config.refresh()
    context = get_user_context()

    quotes = [
        Quote("You cannot change what you are, only what you do.", "Philip Pullman"),
    ]

    greeting = feature_manager.get_variant("Greeting", context["user"])
    greeting_message = ""
    if greeting:
        greeting_message = greeting.configuration

    context["model"] = {}
    context["model"]["greeting_message"] = greeting_message
    context["model"]["quote"] = {}
    context["model"]["quote"] = random.choice(quotes)
    context["isAuthenticated"] = current_user.is_authenticated

    return render_template("index.html", **context)

@bp.route("/heart", methods=["POST"])
def heart():
    if current_user.is_authenticated:
        user = current_user.username
        
        # Track the appropriate event based on the action
        track_event("Liked", user)
    return jsonify({"status": "success"})

@bp.route("/privacy", methods=["GET"])
def privacy():
    return render_template("privacy.html", **get_user_context())

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = Users(request.form.get("username"), hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            flash("Username already exists")
            return redirect(url_for("pages.register"))
        login_user(user)

        return redirect(url_for("pages.index"))
    return render_template("sign_up.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        password = request.form.get("password")
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("pages.index"))
    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("pages.index"))


def get_user_context():
    context = {}
    context["isAuthenticated"] = current_user.is_authenticated
    if current_user.is_authenticated:
        user = current_user.username
        context["user"] = user
    else:
        context["user"] = "Guest"
    return context
