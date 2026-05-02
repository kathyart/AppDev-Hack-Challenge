BeFit!: A daily outfit-sharing app for Cornell students!

Andorid Repo: https://github.com/ashley-ong/BeFit 

App Description:
BeFit is a social platform in which students can share their daily outfits each morning. Users can post their ourfits, browse what others are wearing depending on the weather, and interact with posts through likes. The app also features a leaderboard of the most-liked fits, giving students inspiration and helping them decide what to wear!

How app addresses Backend requirements:
* BeFit utilizes 6 tables including Users, Outfits, Likes, Closet Items, Outfit Combinations, as well as Borrow Request/Offers. Some key relationships between the models include:
    * User -> Outfits: One-to-Many - Each user can post many outfits, and each outfit belongs to exactly one user
    * Users + Outfits + Likes: Many-to-Many - A user can like many outfits, and an outfit can be liked by many users
    * Outfit Combinations -> Closet Items: Many-to-Many - A saved outfit combination can include multiple closet items, and a closet item can appear in multiple combinations.
* API Specification explaining each implemented route (4+): https://docs.google.com/document/d/113-dFCJcfBlNniF1WQA9KFsGr6zpnr5EL_td1w62mHA/edit?usp=sharing

Deployed Backend Url: http://34.182.252.198/
Note: No default route is implemented, but works with the other routes like /users/, /outfits/, etc
<img width="2860" height="550" alt="image" src="https://github.com/user-attachments/assets/bcd92727-8e20-4792-9fa2-b0a38df62faa" />


(Midpoint explanation of database & API design: <img width="300" height="100" alt="Screenshot 2026-04-26 203700" src="https://github.com/user-attachments/assets/5d8f96bd-cc76-40af-ac84-60367acee890" />)


