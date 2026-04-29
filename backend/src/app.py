import json

from db import db, Outfit, User, Like
from flask import Flask, request
from datetime import datetime

# define db filename
db_filename = "befit.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code



# outfits endpoints
@app.route("/outfits/", methods=["GET"])
def get_all_outfits():
    outfits = Outfit.query.all()
    return success_response({"outfits": [o.serialize() for o in outfits]})


@app.route("/outfits/<int:outfit_id>/", methods=["GET"])
def get_outfit_by_outfit_id(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    if outfit is None:
        return failure_response("Outfit not found")
    return success_response(outfit.serialize())


@app.route("/outfits/date/<string:date>/", methods=["GET"])
def get_outfits_by_date(date):
    # the format of the date should be YYYY-MM-DD, for example: /outfits/date/2025-04-29/
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return failure_response("Invalid date format, use YYYY-MM-DD", 400)
    
    outfits = Outfit.query.filter(db.func.date(Outfit.timestamp) == target_date).all()

    if not outfits:
        return failure_response("No outfits found for this date")
    return success_response({"outfits": [o.serialize() for o in outfits]})


@app.route("/outfits/", methods=["POST"])
def create_outfit():
    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    image_url = body.get("image_url")
    user_id = body.get("user_id")
    

    if not image_url or not user_id:
        return failure_response("Missing required fields: image_url and user_id", 400)

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    new_outfit = Outfit(
        image_url=image_url,
        user_id=user_id,
        description=body.get("description", ""),
        weather=body.get("weather"),
        temperature=body.get("temperature")
    )
    db.session.add(new_outfit)
    db.session.commit()
    return success_response(new_outfit.serialize(), 201)


@app.route("/outfits/<int:outfit_id>/", methods=["POST"])
def update_outfit(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    if outfit is None:
        return failure_response("Outfit not found")

    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    if "image_url" in body:
        outfit.image_url = body["image_url"]
    if "description" in body:
        outfit.description = body["description"]
    if "weather" in body:
        outfit.weather = body["weather"]
    if "temperature" in body:
        outfit.temperature = body["temperature"]
    
    db.session.commit()
    return success_response(outfit.serialize())


@app.route("/outfits/<int:outfit_id>/", methods=["DELETE"])
def delete_outfit(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    if outfit is None:
        return failure_response("Outfit not found")

    db.session.delete(outfit)
    db.session.commit()
    return success_response(outfit.serialize())

    





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
