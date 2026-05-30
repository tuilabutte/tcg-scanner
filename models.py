from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )

    profile_picture = db.Column(
        db.String(300),
        default="default-avatar.png"
    )

    bio = db.Column(
        db.Text,
        default=""
    )


class PokemonCard(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    pokemon_type = db.Column(
        db.String(100),
        nullable=False
    )

    rarity = db.Column(
        db.String(100),
        nullable=False
    )


class UserCollection(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    pokemon_card_id = db.Column(
        db.Integer,
        db.ForeignKey("pokemon_card.id"),
        nullable=False
    )
