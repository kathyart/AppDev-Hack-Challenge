from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Like(db.Model):
    """
    Like Model
    """

    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    outfit_id = db.Column(db.Integer, db.ForeignKey("outfits.id"), nullable=False)

    def __init__(self, user_id, outfit_id):
        """
        Initializes a Like object
        """
        self.user_id = user_id
        self.outfit_id = outfit_id

    def serialize(self):
        """
        Serializes a Like object
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "outfit_id": self.outfit_id
        }


class User(db.Model):
    """
    User Model
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    bio = db.Column(db.String, default="")
    netid = db.Column(db.String, nullable=False, unique=True)
    
    outfits = db.relationship("Outfit", back_populates="user", cascade="delete")
    likes = db.relationship("Like", backref="user", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initializes an User object
        """
        self.name = kwargs.get("name", "")
        self.bio = kwargs.get("bio", "")
        self.netid = kwargs.get("netid", "")


    def serialize(self):
        """
        Serializes an User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "bio": self.bio,
            "outfits": [o.simple_serialize() for o in self.outfits]
        }
    
    def simple_serialize(self):
        """
        Simply serailizes an User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }

class Outfit(db.Model):
    """
    Outfit Model (represents a single outfit post)
    """

    __tablename__ = "outfits"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_url = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    weather = db.Column(db.String, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="outfits")

    likes = db.relationship("Like", backref="outfit", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initalizes an Outfit object
        """
        self.image_url = kwargs.get("image_url")
        self.description = kwargs.get("description", "")
        self.weather = kwargs.get("weather")
        self.temperature = kwargs.get("temperature")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        """
        Serializes an Outfit object
        """
        return {
            "id": self.id,
            "image_url": self.image_url,
            "description": self.description,
            "weather": self.weather,
            "temperature": self.temperature,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user.simple_serialize(),
            "likes": len(self.likes)
        }

    def simple_serialize(self):
        """
        Simply serializes an Outfit Object
        """
        return {
            "id": self.id,
            "image_url": self.image_url,
            "timestamp": self.timestamp.isoformat()
        }
    




    
