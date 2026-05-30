from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from functools import wraps
from werkzeug.utils import secure_filename

from auth.auth import auth

from models import (
    db,
    User,
    PokemonCard,
    UserCollection
)

import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "pokemon-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tcg-scanner.db"
app.config["UPLOAD_FOLDER"] = os.path.join(
    "static",
    "images",
    "profiles"
)

db.init_app(app)


# LOGIN REQUIRED
def login_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


# CREATE DATABASE
with app.app_context():

    db.create_all()

    pokemon_data = [

        ("Tyrantrum", "Dragon", "Rare"),
        ("Ariados", "Bug", "Common"),
        ("Binacle", "Rock", "Common"),
        ("Diggersby", "Normal", "Uncommon"),
        ("Gengar", "Ghost", "Rare"),
        ("Rowlet", "Grass", "Starter"),
        ("Aegislash", "Steel", "Rare"),
        ("Scatterbug", "Bug", "Common"),
        ("Aromatisse", "Fairy", "Rare"),
        ("Staryu", "Water", "Common"),
        ("Talonflame", "Fire", "Rare"),
        ("Klefki", "Steel", "Uncommon"),
        ("Fletchinder", "Fire", "Uncommon"),
        ("Fletchling", "Normal", "Common")

    ]

    for pokemon in pokemon_data:

        existing = PokemonCard.query.filter_by(
            name=pokemon[0]
        ).first()

        if not existing:

            db.session.add(
                PokemonCard(
                    name=pokemon[0],
                    pokemon_type=pokemon[1],
                    rarity=pokemon[2]
                )
            )

    db.session.commit()


# BLUEPRINT
app.register_blueprint(auth)


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# SCANNER
@app.route("/scanner")
@login_required
def scanner():
    return render_template("scanner.html")


# COLLECTION
@app.route("/collection")
@login_required
def collection():

    collection_cards = UserCollection.query.filter_by(
        user_id=session["user_id"]
    ).all()

    cards = []

    for item in collection_cards:

        pokemon = PokemonCard.query.get(
            item.pokemon_card_id
        )

        cards.append(pokemon)

    progress_percentage = round(
        (len(cards) / 1025) * 100,
        2
    )

    return render_template(
        "collection.html",
        cards=cards,
        progress_percentage=progress_percentage
    )


# SEARCH
@app.route("/search")
def search():
    return render_template("search.html")


# PROFILE
@app.route("/profile/<int:user_id>")
def profile(user_id):

    user = User.query.get(user_id)

    if not user:
        return redirect(url_for("home"))

    collection_cards = UserCollection.query.filter_by(
        user_id=user_id
    ).all()

    cards = []

    for item in collection_cards:

        pokemon = PokemonCard.query.get(
            item.pokemon_card_id
        )

        cards.append(pokemon)

    return render_template(
        "profile.html",
        user=user,
        cards=cards
    )


# EDIT PROFILE
@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    user = User.query.get(
        session["user_id"]
    )

    if request.method == "POST":

        user.bio = request.form.get(
            "bio",
            ""
        )

        profile_picture = request.files.get(
            "profile_picture"
        )

        if (
            profile_picture and
            profile_picture.filename != ""
        ):

            filename = secure_filename(
                profile_picture.filename
            )

            save_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            profile_picture.save(
                save_path
            )

            user.profile_picture = filename

        db.session.commit()

        return redirect(
            url_for(
                "profile",
                user_id=user.id
            )
        )

    return render_template(
        "edit_profile.html",
        user=user
    )


# SEARCH USERS API
@app.route("/api/search-users")
def search_users():

    query = request.args.get("q", "")

    users = User.query.filter(
        User.username.contains(query)
    ).limit(10).all()

    return jsonify([
        {
            "id": user.id,
            "username": user.username,
            "profile_picture": user.profile_picture
        }
        for user in users
    ])


# SCAN API
@app.route("/api/scan", methods=["POST"])
def api_scan():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        })

    data = request.get_json()

    pokemon_name = data.get(
        "pokemon_name"
    )

    pokemon = PokemonCard.query.filter_by(
        name=pokemon_name
    ).first()

    if not pokemon:

        return jsonify({
            "success": False,
            "message": "Unknown Pokémon."
        })

    existing = UserCollection.query.filter_by(
        user_id=session["user_id"],
        pokemon_card_id=pokemon.id
    ).first()

    if existing:

        return jsonify({
            "success": False,
            "message":
            f"{pokemon_name} already collected."
        })

    new_entry = UserCollection(
        user_id=session["user_id"],
        pokemon_card_id=pokemon.id
    )

    db.session.add(
        new_entry
    )

    db.session.commit()

    return jsonify({
        "success": True,
        "message":
        f"{pokemon_name} added to collection!"
    })


if __name__ == "__main__":
    app.run(debug=True)
