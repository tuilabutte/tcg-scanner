from werkzeug.security import generate_password_hash

from app import app

from models import (
db,
User,
PokemonCard,
UserCollection,
TradePost,
TradeComment
)

with app.app_context():

#USERS

    test_users = [

        (
            "ProfessorOak",
            "pokemon123",
            "Pokémon researcher studying rare species."
        ),

        (
            "AshKetchum",
            "pokemon123",
            "Future Pokémon Master."
        ),

        (
            "Misty",
            "pokemon123",
            "Water Pokémon specialist."
        ),

        (
            "Brock",
            "pokemon123",
            "Rock type trainer and breeder."
        ),

        (
            "GaryOak",
            "pokemon123",
            "Collecting Pokémon faster than Ash."
        )

    ]

    for username, password, bio in test_users:

        existing = User.query.filter_by(
            username=username
        ).first()

        if not existing:

            db.session.add(
                User(
                    username=username,
                    password=generate_password_hash(password),
                    profile_picture="default-avatar.png",
                    bio=bio
                )
            )

    db.session.commit()

#COLLECTIONS

    collections = {

        "ProfessorOak": [
            "Tyrantrum",
            "Ariados",
            "Binacle",
            "Diggersby",
            "Gengar",
            "Rowlet",
            "Aegislash",
            "Scatterbug",
            "Aromatisse",
            "Staryu",
            "Talonflame",
            "Klefki",
            "Fletchinder",
            "Fletchling"
        ],

        "AshKetchum": [
            "Gengar",
            "Rowlet",
            "Talonflame",
            "Fletchling"
        ],

        "Misty": [
            "Staryu",
            "Aromatisse"
        ],

        "Brock": [
            "Binacle",
            "Tyrantrum"
        ],

        "GaryOak": [
            "Aegislash",
            "Klefki",
            "Fletchinder"
        ]

    }

    for username, pokemon_list in collections.items():

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:
            continue

        for pokemon_name in pokemon_list:

            card = PokemonCard.query.filter_by(
                name=pokemon_name
            ).first()

            if not card:
                continue

            existing = UserCollection.query.filter_by(
                user_id=user.id,
                pokemon_card_id=card.id
            ).first()

            if not existing:

                db.session.add(
                    UserCollection(
                        user_id=user.id,
                        pokemon_card_id=card.id
                    )
                )

    db.session.commit()

#TRADE POSTS

    sample_posts = [

        (
            "AshKetchum",
            "Looking for Aegislash. Offering Talonflame."
        ),

        (
            "Misty",
            "Need a Rowlet for my collection. Happy to trade Staryu."
        ),

        (
            "GaryOak",
            "Trading Klefki and Fletchinder. Looking for rare Pokémon."
        ),

        (
            "ProfessorOak",
            "Research project: seeking all Pokémon for documentation."
        )

    ]

    for username, content in sample_posts:

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:
            continue

        existing = TradePost.query.filter_by(
            user_id=user.id,
            content=content
        ).first()

        if not existing:

            db.session.add(
                TradePost(
                    user_id=user.id,
                    content=content
                )
            )

    db.session.commit()

#COMMENTS

    posts = TradePost.query.order_by(
        TradePost.id.asc()
    ).all()

    if len(posts) >= 4:

        sample_comments = [

            (
                "GaryOak",
                posts[0].id,
                "I might have one available."
            ),

            (
                "Misty",
                posts[0].id,
                "Good luck with that trade!"
            ),

            (
                "AshKetchum",
                posts[1].id,
                "I'd definitely trade for Rowlet."
            ),

            (
                "ProfessorOak",
                posts[2].id,
                "Interesting offer."
            ),

            (
                "Brock",
                posts[3].id,
                "Happy to help the research effort."
            )

        ]

        for username, post_id, content in sample_comments:

            user = User.query.filter_by(
                username=username
            ).first()

            if not user:
                continue

            existing = TradeComment.query.filter_by(
                user_id=user.id,
                post_id=post_id,
                content=content
            ).first()

            if not existing:

                db.session.add(
                    TradeComment(
                        user_id=user.id,
                        post_id=post_id,
                        content=content
                    )
                )

    db.session.commit()

    print("Seeding complete.")