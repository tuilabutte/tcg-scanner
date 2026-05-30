from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from models import (
    db,
    User
)

import os

auth = Blueprint(
    "auth", 
    __name__,
    url_prefix="/auth",
    template_folder="templates"
)

#REGISTER
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        profile_picture = request.files.get(
            "profile_picture"
        )

        if not username or not password:

            flash(
                "Please fill in all fields.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash(
                "Username already exists.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        hashed_password = generate_password_hash(
            password
        )

        filename = "default-avatar.png"

        #SAVE PROFILE PICTURE
        if profile_picture and profile_picture.filename != "":

            filename = secure_filename(
                profile_picture.filename
            )

            save_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )

            profile_picture.save(save_path)

        new_user = User(
            username=username,
            password=hashed_password,
            profile_picture=filename
        )

        db.session.add(new_user)

        db.session.commit()

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template("auth/register.html")


#LOGIN
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id
            session["username"] = user.username

            flash(
                "Logged in successfully.",
                "success"
            )

            return redirect(
                url_for("home")
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template("auth/login.html")


#LOGOUT
@auth.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect(url_for("home"))
