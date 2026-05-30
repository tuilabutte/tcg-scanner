from werkzeug.security import generate_password_hash

from app import app

from models import (
    db,
    User,
    PokemonCard,
    UserCollection
)

with app.app_context():

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

            user = User(
                username=username,
                password=generate_password_hash(password),
                profile_picture="default-avatar.png",
                bio=bio
            )

            db.session.add(user)

    db.session.commit()

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

    print("Seeding complete.")