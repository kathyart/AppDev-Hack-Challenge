from db import db, User, Outfit, Like
from app import app
from datetime import datetime, timezone

with app.app_context():
    db.drop_all()
    db.create_all()

    users = [
        User(name="Frank Wu", netid="fw987", bio="Interested in streetwear!"),
        User(name="David Chen", netid="dc321", bio="Love minimalist fits"),
        User(name="Carla Gomez", netid="cg789", bio="Vintage fashion"),
        User(name="Raahi Menon", netid="rm456", bio="Love fall outfits"),
        User(name="Emily Shay", netid="es654", bio="Colorful outfits"),
        User(name="Alexa Kim", netid="ak123", bio="Love to wear athletic wear!"),
    ]
    db.session.add_all(users)
    db.session.commit()

    outfits = [
        Outfit(image_url="https://images.unsplash.com/photo-1769689387719-f11faac08cbe", user_id=1, description="Black puffer + cargos", weather="cold", temperature=32),
        Outfit(image_url="https://images.unsplash.com/photo-1616030257764-0fe6a2f05138", user_id=1, description="Oversized hoodie", weather="cool", temperature=55),

        Outfit(image_url="https://images.unsplash.com/photo-1499971856191-1a420a42b498", user_id=2, description="All black minimalist", weather="mild", temperature=60),
        Outfit(image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab", user_id=2, description="White tee + jeans", weather="warm", temperature=72),

        Outfit(image_url="https://images.unsplash.com/photo-1529139574466-a303027c1d8b", user_id=3, description="Vintage denim jacket", weather="cool", temperature=58),
        Outfit(image_url="https://images.unsplash.com/photo-1563178406-4cdc2923acbc", user_id=3, description="Retro floral dress", weather="warm", temperature=75),

        Outfit(image_url="https://images.unsplash.com/photo-1765337210176-1bb643f4776b", user_id=4, description="Cozy layers", weather="cold", temperature=30),
        Outfit(image_url="https://images.unsplash.com/photo-1739169585918-84f6fba6c6f7", user_id=4, description="Monochrome fit", weather="mild", temperature=65),

        Outfit(image_url="https://images.unsplash.com/photo-1645423967101-a052e10a4312", user_id=5, description="Pink sweater + skirt", weather="cool", temperature=52),
        Outfit(image_url="https://images.unsplash.com/photo-1512436991641-6745cdb1723f", user_id=5, description="Spring outfit", weather="warm", temperature=78),

        Outfit(image_url="https://images.unsplash.com/photo-1721969982799-fb9a78c43e7f", user_id=6, description="Gym fit", weather="mild", temperature=68),
        Outfit(image_url="https://images.unsplash.com/photo-1509833903111-9cb142f644e4", user_id=6, description="Running outfit", weather="warm", temperature=80),
    ]
    db.session.add_all(outfits)
    db.session.commit()


    likes = [
        Like(user_id=1, outfit_id=3), Like(user_id=1, outfit_id=4), Like(user_id=1, outfit_id=5),
        Like(user_id=2, outfit_id=1), Like(user_id=2, outfit_id=2), Like(user_id=2, outfit_id=9),
        Like(user_id=3, outfit_id=7), Like(user_id=3, outfit_id=11), Like(user_id=3, outfit_id=12),
        Like(user_id=4, outfit_id=1), Like(user_id=4, outfit_id=5), Like(user_id=4, outfit_id=6),
        Like(user_id=5, outfit_id=3), Like(user_id=5, outfit_id=11), Like(user_id=5, outfit_id=12),
        Like(user_id=6, outfit_id=9), Like(user_id=6, outfit_id=10), Like(user_id=6, outfit_id=6),
    ]
    db.session.add_all(likes)
    db.session.commit()

 