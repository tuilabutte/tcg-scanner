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
    UserCollection,
    TradePost,
    TradeComment
)

import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "pokemon-secret-key"
import os

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASE_DIR, 'tcg-scanner.db')}"
)

app.config["UPLOAD_FOLDER"] = os.path.join(
    "static",
    "images",
    "profiles"
)

db.init_app(app)


#LOGIN REQUIRED
def login_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


#CREATE DATABASE
with app.app_context():

    db.create_all()

    pokemon_data = [

    ("Tyrantrum", "Dragon", "Rare",
     "A powerful prehistoric Dragon Pokémon with crushing jaws."),

    ("Ariados", "Bug", "Common",
     "A spider Pokémon that traps prey using strong silk."),

    ("Binacle", "Rock", "Common",
     "Two Pokémon living together on a single rock."),

    ("Diggersby", "Normal", "Uncommon",
     "Uses its massive ears to dig tunnels with ease."),

    ("Gengar", "Ghost", "Rare",
     "A mischievous Ghost Pokémon that hides in shadows."),

    ("Rowlet", "Grass", "Starter",
     "A curious owl Pokémon that attacks with sharp leaves."),

    ("Aegislash", "Steel", "Rare",
     "A royal sword Pokémon said to control kings."),

    ("Scatterbug", "Bug", "Common",
     "A small Bug Pokémon that protects itself with powder."),

    ("Aromatisse", "Fairy", "Rare",
     "Uses powerful fragrances to calm and support allies."),

    ("Staryu", "Water", "Common",
     "A mysterious star-shaped Pokémon from the ocean."),

    ("Talonflame", "Fire", "Rare",
     "A blazing bird Pokémon capable of incredible speed."),

    ("Klefki", "Steel", "Uncommon",
     "Collects keys and stores them on its ring."),

    ("Fletchinder", "Fire", "Uncommon",
     "The evolved form of Fletchling with stronger flames."),

    ("Fletchling", "Normal", "Common",
     "A tiny bird Pokémon known for its cheerful song.")

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
                    rarity=pokemon[2],
                    description=pokemon[3]
                )
            )

    db.session.commit()

#BLUEPRINT
app.register_blueprint(auth)

#HOME
@app.route("/")
def home():
    return render_template("index.html")

# SCANNER
@app.route("/scanner")
@login_required
def scanner():
    return render_template("scanner.html")

#COLLECTION
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

        if pokemon:

            pokemon.collector_count = (
                UserCollection.query.filter_by(
                    pokemon_card_id=pokemon.id
                ).count()
            )

            cards.append(pokemon)

    TOTAL_POKEMON = 14

    progress_percentage = round(
        (len(cards) / TOTAL_POKEMON) * 100,
        2
    )

    return render_template(
        "collection.html",
        cards=cards,
        progress_percentage=progress_percentage,
        total_pokemon=TOTAL_POKEMON
    )

#SEARCH
@app.route("/search")
def search():
    return render_template("search.html")

#PROFILE
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

#TRADING HUB
@app.route("/trading-hub")
@login_required
def trading_hub():

    posts = TradePost.query.order_by(
        TradePost.created_at.desc()
    ).all()

    return render_template(
        "trading_hub.html",
        posts=posts,
        User=User,
        TradeComment=TradeComment
    )

#CREATE TRADE POST
@app.route(
    "/create-trade-post",
    methods=["POST"]
)
@login_required
def create_trade_post():

    content = request.form.get(
        "content",
        ""
    ).strip()

    if not content:

        return redirect(
            url_for("trading_hub")
        )

    new_post = TradePost(
        user_id=session["user_id"],
        content=content
    )

    db.session.add(new_post)
    db.session.commit()

    return redirect(
        url_for("trading_hub")
    )

#COMMENT ON TRADE POST
@app.route(
    "/comment-trade-post/<int:post_id>",
    methods=["POST"]
)
@login_required
def comment_trade_post(post_id):

    content = request.form.get(
        "comment_content",
        ""
    ).strip()

    if not content:

        return redirect(
            url_for("trading_hub")
        )

    comment = TradeComment(
        user_id=session["user_id"],
        post_id=post_id,
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return redirect(
        url_for("trading_hub")
    )

@app.route(
    "/delete-trade-comment/<int:comment_id>",
    methods=["POST"]
)
@login_required
def delete_trade_comment(comment_id):

    comment = TradeComment.query.get(
        comment_id
    )

    if (
        comment and
        comment.user_id ==
        session["user_id"]
    ):

        db.session.delete(comment)
        db.session.commit()

    return redirect(
        url_for("trading_hub")
    )

#DELETE TRADE POST
@app.route(
    "/delete-trade-post/<int:post_id>",
    methods=["POST"]
)
@login_required
def delete_trade_post(post_id):

    post = TradePost.query.get(
        post_id
    )

    if (
        post and
        post.user_id ==
        session["user_id"]
    ):

        comments = TradeComment.query.filter_by(
            post_id=post.id
        ).all()

        for comment in comments:

            db.session.delete(comment)

        db.session.delete(post)

        db.session.commit()

    return redirect(
        url_for("trading_hub")
    )

#EDIT PROFILE
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


#SEARCH USERS
@app.route("/api/search-users")
def search_users():

    query = request.args.get(
        "q",
        ""
    )

    users = User.query.filter(
        User.username.contains(query)
    ).all()

    results = []

    for user in users:

        collection_count = (
            UserCollection.query.filter_by(
                user_id=user.id
            ).count()
        )

        results.append(
            {
                "id": user.id,
                "username": user.username,
                "profile_picture": user.profile_picture,
                "bio": user.bio,
                "collection_count": collection_count
            }
        )

    return jsonify(results)

#SCAN 
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