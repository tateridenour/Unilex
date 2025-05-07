import sqlite3

path = "data/claims.db"
con = sqlite3.connect(path)
cur = con.cursor()

cur.execute("DROP TABLE claims")
cur.execute("""
    CREATE TABLE claims(
        article_id UNIQUE PRIMARY KEY,
        user_id,
        selected_image,
        position,
        is_star,
        is_tag1,
        is_tag2,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
""")
