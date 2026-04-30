import json
import os

from db import db, Outfit, User, Like, ClothingItem, OutfitCombination
from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta

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

# local folder for uploaded images
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


#------------------------------------------------
# OUTFIT ROUTES (8)
# -----------------------------------------------

# Get all outfits
@app.route("/outfits/", methods=["GET"])
def get_all_outfits():
    outfits = Outfit.query.all()
    return success_response({"outfits": [o.serialize() for o in outfits]})

# Get one outfit
@app.route("/outfits/<int:outfit_id>/", methods=["GET"])
def get_outfit_by_outfit_id(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    if outfit is None:
        return failure_response("Outfit not found")
    return success_response(outfit.serialize())

# Get outfits by date
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


# Get outfits by weather (case-insensitive, partial match)
@app.route("/outfits/weather/<string:weather>/", methods=["GET"])
def get_outfits_by_weather(weather):
    # search outfits where weather matches (ilike)
    outfits = Outfit.query.filter(Outfit.weather.ilike(f"%{weather}%")).all()

    if not outfits:
        return failure_response("No outfits found for this weather")
    return success_response({"outfits": [o.serialize() for o in outfits]})


# Get outfits by temperature range (query params: min, max)
@app.route("/outfits/temperature/", methods=["GET"])
def get_outfits_by_temperature_range():
    # read min and max from query string
    min_raw = request.args.get("min")
    max_raw = request.args.get("max")

    if min_raw is None or max_raw is None:
        return failure_response("Missing required query parameters: min and max", 400)

    # convert to floats
    try:
        min_temp = float(min_raw)
        max_temp = float(max_raw)
    except ValueError:
        return failure_response("Temperature values must be numbers", 400)

    # outfits with temperature between min and max (inclusive)
    outfits = Outfit.query.filter(
        Outfit.temperature >= min_temp,
        Outfit.temperature <= max_temp,
    ).all()

    if not outfits:
        return failure_response("No outfits found in this temperature range")
    return success_response({"outfits": [o.serialize() for o in outfits]})


# Create an outfit
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

    # one outfit per user per day (compare date in UTC)
    today_utc = datetime.now(timezone.utc).date()
    already_posted_today = Outfit.query.filter(
        Outfit.user_id == user_id,
        db.func.date(Outfit.timestamp) == today_utc,
    ).first()
    if already_posted_today is not None:
        return failure_response("User has already posted an outfit today", 400)

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

# Update an outfit
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

# Delete an outfit
@app.route("/outfits/<int:outfit_id>/", methods=["DELETE"])
def delete_outfit(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    if outfit is None:
        return failure_response("Outfit not found")

    db.session.delete(outfit)
    db.session.commit()
    return success_response(outfit.serialize())

#------------------------------------------------
# USER ROUTES (5)
# -----------------------------------------------

# GET all users
@app.route("/users/", methods=["GET"])
def get_all_users():
    # get all users
    users = User.query.all()

    # return serialized users
    return success_response({"users": [user.serialize() for user in users]})

# GET one specfic user
@app.route("/users/<int:user_id>/", methods=["GET"])
def get_user_by_user_id(user_id):
    # get user by id
    user = User.query.filter_by(id=user_id).first()

    # check if user exists
    if user is None:
        return failure_response("User not found")

    # return serialized user
    return success_response(user.serialize())

# Create a new user
@app.route("/users/", methods=["POST"])
def create_user():
    # get request body
    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    # get required and optional fields
    name = body.get("name")
    netid = body.get("netid")
    bio = body.get("bio", "")

    # check required fields
    if not name or not netid:
        return failure_response("Missing required fields: name and netid", 400)

    # check if netid already exists
    existing_user = User.query.filter_by(netid=netid).first()
    if existing_user is not None:
        return failure_response("User with this netid already exists", 400)

    # create new user
    new_user = User(name=name, netid=netid, bio=bio)
    db.session.add(new_user)
    db.session.commit()

    # return created user
    return success_response(new_user.serialize(), 201)

# GET all outfits from a specific user
@app.route("/users/<int:user_id>/outfits/", methods=["GET"])
def get_outfits_by_user_id(user_id):
    # get user by id
    user = User.query.filter_by(id=user_id).first()

    # check if user exists
    if user is None:
        return failure_response("User not found")

    # get user's outfits, newest first
    outfits = Outfit.query.filter_by(user_id=user_id).order_by(Outfit.timestamp.desc()).all()

    # return serialized outfits
    return success_response({"outfits": [outfit.serialize() for outfit in outfits]})

# GET all outfits a specfic user liked
@app.route("/users/<int:user_id>/likes/", methods=["GET"])
def get_liked_outfits_by_user_id(user_id):
    # get user by id
    user = User.query.filter_by(id=user_id).first()

    # check if user exists
    if user is None:
        return failure_response("User not found")

    # get outfits this user has liked
    outfits = [like.outfit for like in user.likes]

    # return serialized liked outfits
    return success_response({"outfits": [outfit.serialize() for outfit in outfits]})

#------------------------------------------------
# LIKE ROUTES (3)
# -----------------------------------------------

# Like an Outfit
@app.route("/likes/", methods=["POST"])
def create_like():
    # get request body
    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    user_id = body.get("user_id")
    outfit_id = body.get("outfit_id")

    # check if user_id and outfit_id are provided
    if user_id is None or outfit_id is None:
        return failure_response("Missing required fields: user_id and outfit_id", 400)

    # check if user exists
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    # check if outfit exists
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    if outfit is None:
        return failure_response("Outfit not found")

    # check if the user has already liked this outfit
    existing_like = Like.query.filter_by(user_id=user_id, outfit_id=outfit_id).first()
    if existing_like is not None:
        return failure_response("User has already liked this outfit", 400)

    # create new like
    new_like = Like(user_id=user_id, outfit_id=outfit_id)
    db.session.add(new_like)
    db.session.commit()

    # return created like
    return success_response(new_like.serialize(), 201)

# Unlike an Outfit
@app.route("/likes/", methods=["DELETE"])
def delete_like():
    # get request body
    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    user_id = body.get("user_id")
    outfit_id = body.get("outfit_id")

    # check if user_id and outfit_id are provided
    if user_id is None or outfit_id is None:
        return failure_response("Missing required fields: user_id and outfit_id", 400)

    # find the like using user_id and outfit_id
    like = Like.query.filter_by(user_id=user_id, outfit_id=outfit_id).first()
    if like is None:
        return failure_response("Like not found")

    # delete like
    serialized = like.serialize()
    db.session.delete(like)
    db.session.commit()

    # return success response
    return success_response(serialized)

# View like counts
@app.route("/outfits/<int:outfit_id>/likes/", methods=["GET"])
def get_likes_for_outfit(outfit_id):
    # check if outfit exists
    outfit = Outfit.query.filter_by(id=outfit_id).first()
    if outfit is None:
        return failure_response("Outfit not found")

    # get all Like objects for this outfit
    likes = Like.query.filter_by(outfit_id=outfit_id).all()

    # return serialized likes and count
    return success_response(
        {
            "likes": [like.serialize() for like in likes],
            "count": len(likes),
        }
    )

## LEADERBOARD ROUTES (1)
# Weekly leaderboard (top 6 outfits by likes in the last 7 days)
@app.route("/leaderboard/", methods=["GET"])
def get_leaderboard():
    # get current UTC time and start of weekly window
    now_utc = datetime.now(timezone.utc)
    one_week_ago = now_utc - timedelta(days=7)

    # only outfits posted in the last week
    outfits = Outfit.query.filter(Outfit.timestamp >= one_week_ago).all()

    # sort outfits by likes (highest to lowest)
    sorted_outfits = sorted(outfits, key=lambda o: len(o.likes), reverse=True)

    # take top 6
    top_outfits = sorted_outfits[:6]

    # return response
    return success_response(
        {"leaderboard": [outfit.serialize() for outfit in top_outfits]}
    )


## AUTH ROUTES (1)
# Login with netid only (no password)
@app.route("/login/", methods=["POST"])
def login():
    # get request body
    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    netid = body.get("netid")
    if not netid:
        return failure_response("Missing required field: netid", 400)

    # find user by netid
    user = User.query.filter_by(netid=netid).first()
    if user is None:
        return failure_response("User not found", 404)

    return success_response(
        {"message": "Login successful", "user": user.serialize()}
    )


## UPLOAD ROUTES (2)
# Serve a file from the uploads folder
@app.route("/uploads/<string:filename>/", methods=["GET"])
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# Upload an image file; returns image_url for use with POST /outfits/
@app.route("/upload/", methods=["POST"])
def upload_image():
    # check that an image file was sent
    if "image" not in request.files:
        return failure_response("No image file provided", 400)

    file = request.files["image"]

    # check that user selected a file
    if file.filename is None or file.filename == "":
        return failure_response("No selected file", 400)

    # check file extension
    if not allowed_file(file.filename):
        return failure_response("Invalid file type. Use png, jpg, or jpeg", 400)

    # save with a safe filename
    safe_name = secure_filename(file.filename)
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    file.save(upload_path)

    # URL the frontend can use (same host as the API)
    image_url = f"/uploads/{safe_name}/"

    return success_response({"image_url": image_url}, 201)

# ---------------------------------
#  CLOSET ROUTES (3)
# ------------------------------------

# Add a clothing item to closet
@app.route("/users/<int:user_id>/closet/", methods=["POST"])
def add_clothing_item(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    image_url = body.get("image_url")
    category = body.get("category")

    if not image_url or not category:
        return failure_response("Missing required fields: image_url and category", 400)

    VALID_CATEGORIES = {"top", "bottom", "shoes", "outerwear", "accessory"}
    if category not in VALID_CATEGORIES:
        return failure_response(f"Invalid category. Choose from: {', '.join(VALID_CATEGORIES)}", 400)

    item = ClothingItem(user_id=user_id, image_url=image_url, category=category, name=body.get("name", ""))
    db.session.add(item)
    db.session.commit()
    return success_response(item.serialize(), 201)


# Get all clothing items in a user's closet
@app.route("/users/<int:user_id>/closet/", methods=["GET"])
def get_closet(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    items = ClothingItem.query.filter_by(user_id=user_id).all()
    return success_response({"items": [item.serialize() for item in items]})


# Delete a clothing item
@app.route("/closet/<int:item_id>/", methods=["DELETE"])
def delete_clothing_item(item_id):
    item = ClothingItem.query.filter_by(id=item_id).first()
    if item is None:
        return failure_response("Clothing item not found")

    db.session.delete(item)
    db.session.commit()
    return success_response(item.serialize())


# --------------------------------------
# OUTFIT COMBINATION ROUTES (3)
# --------------------------------------

# Save a new outfit combination
@app.route("/users/<int:user_id>/combinations/", methods=["POST"])
def create_combination(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    body = request.json
    if body is None:
        return failure_response("Invalid request body", 400)

    item_ids = body.get("item_ids")  # list of ClothingItem IDs
    if not item_ids or not isinstance(item_ids, list):
        return failure_response("Missing required field: item_ids (must be a list)", 400)

    items = ClothingItem.query.filter(ClothingItem.id.in_(item_ids)).all()
    if len(items) != len(item_ids):
        return failure_response("One or more clothing items not found", 404)

    combo = OutfitCombination(user_id=user_id, name=body.get("name", ""))
    combo.items = items
    db.session.add(combo)
    db.session.commit()
    return success_response(combo.serialize(), 201)


# Get all saved combinations for a user
@app.route("/users/<int:user_id>/combinations/", methods=["GET"])
def get_combinations(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    combos = OutfitCombination.query.filter_by(user_id=user_id).all()
    return success_response({"combinations": [c.serialize() for c in combos]})


# Delete a combination
@app.route("/combinations/<int:combination_id>/", methods=["DELETE"])
def delete_combination(combination_id):
    combo = OutfitCombination.query.filter_by(id=combination_id).first()
    if combo is None:
        return failure_response("Combination not found")

    db.session.delete(combo)
    db.session.commit()
    return success_response(combo.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
