import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

sql = """
DROP TABLE IF EXISTS user_reviews CASCADE;
DROP TABLE IF EXISTS reviews_summary CASCADE;
DROP TABLE IF EXISTS prices CASCADE;
DROP TABLE IF EXISTS game_genres CASCADE;
DROP TABLE IF EXISTS genres CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS developers CASCADE;

CREATE TABLE developers (
    developer_id SERIAL PRIMARY KEY,
    developer_name TEXT UNIQUE NOT NULL
);

CREATE TABLE games (
    app_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    release_date DATE,
    developer_id INTEGER REFERENCES developers(developer_id),
    short_description TEXT,
    required_age INTEGER,
    average_playtime INTEGER,
    median_playtime INTEGER,
    owners TEXT,
    positive_ratings INTEGER,
    negative_ratings INTEGER
);

CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name TEXT UNIQUE NOT NULL
);

CREATE TABLE game_genres (
    app_id INTEGER REFERENCES games(app_id),
    genre_id INTEGER REFERENCES genres(genre_id),
    PRIMARY KEY (app_id, genre_id)
);

CREATE TABLE prices (
    app_id INTEGER PRIMARY KEY REFERENCES games(app_id),
    price NUMERIC(10,2),
    initial_price NUMERIC(10,2),
    is_free BOOLEAN
);

CREATE TABLE reviews_summary (
    app_id INTEGER PRIMARY KEY REFERENCES games(app_id),
    positive_ratings INTEGER,
    negative_ratings INTEGER,
    positive_ratio NUMERIC(5,2),
    total_reviews INTEGER
);
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()
    print("All tables created successfully!")
    