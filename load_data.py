import os
import json
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

# ── Load raw data ──────────────────────────────────────────
print("Loading raw data...")
with open("data/raw_games.json") as f:
    games = json.load(f)

print(f"Processing {len(games)} games...")

# ── Build flat records ─────────────────────────────────────
records = []
for g in games:
    d = g.get("steam_details", {})
    
    price_info = d.get("price_overview", {})
    release = d.get("release_date", {}).get("date", None)
    devs = d.get("developers", ["Unknown"])[0] if d.get("developers") else "Unknown"
    genres = [x["description"] for x in d.get("genres", [])]
    
    records.append({
        "app_id": g["appid"],
        "name": g["name"],
        "developer": devs,
        "release_date": release,
        "short_description": d.get("short_description", ""),
        "required_age": d.get("required_age", 0),
        "average_playtime": g.get("average_forever", 0),
        "median_playtime": g.get("median_forever", 0),
        "owners": g.get("owners", ""),
        "positive_ratings": g.get("positive", 0),
        "negative_ratings": g.get("negative", 0),
        "price": price_info.get("final", 0) / 100 if price_info else 0,
        "initial_price": price_info.get("initial", 0) / 100 if price_info else 0,
        "is_free": d.get("is_free", False),
        "genres": genres
    })

df = pd.DataFrame(records)
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

# ── Load developers ────────────────────────────────────────
print("Loading developers...")
devs_df = pd.DataFrame({"developer_name": df["developer"].unique()})
devs_df.to_sql("developers", engine, if_exists="append", index=False)
devs_db = pd.read_sql("SELECT * FROM developers", engine)

# ── Load games ─────────────────────────────────────────────
print("Loading games...")
games_df = df.merge(devs_db, left_on="developer", right_on="developer_name", how="left")
games_table = games_df[[
    "app_id", "name", "release_date", "developer_id",
    "short_description", "required_age", "average_playtime",
    "median_playtime", "owners", "positive_ratings", "negative_ratings"
]]
games_table.to_sql("games", engine, if_exists="append", index=False)

# ── Load genres ────────────────────────────────────────────
print("Loading genres...")
all_genres = set(g for genres in df["genres"] for g in genres)
genres_df = pd.DataFrame({"genre_name": list(all_genres)})
genres_df.to_sql("genres", engine, if_exists="append", index=False)
genres_db = pd.read_sql("SELECT * FROM genres", engine)

# ── Load game_genres ───────────────────────────────────────
print("Loading game genres...")
rows = []
for _, row in df.iterrows():
    for genre in row["genres"]:
        match = genres_db[genres_db["genre_name"] == genre]
        if not match.empty:
            rows.append({
                "app_id": row["app_id"],
                "genre_id": int(match.iloc[0]["genre_id"])
            })
game_genres_df = pd.DataFrame(rows).drop_duplicates()
game_genres_df.to_sql("game_genres", engine, if_exists="append", index=False)

# ── Load prices ────────────────────────────────────────────
print("Loading prices...")
prices_df = df[["app_id", "price", "initial_price", "is_free"]]
prices_df.to_sql("prices", engine, if_exists="append", index=False)

# ── Load reviews_summary ───────────────────────────────────
print("Loading reviews...")
rev_df = df[["app_id", "positive_ratings", "negative_ratings"]].copy()
rev_df["total_reviews"] = rev_df["positive_ratings"] + rev_df["negative_ratings"]
rev_df["positive_ratio"] = (
    rev_df["positive_ratings"] / rev_df["total_reviews"].replace(0, 1)
) * 100
rev_df = rev_df.round({"positive_ratio": 2})
rev_df.to_sql("reviews_summary", engine, if_exists="append", index=False)

print("\n✅ All data loaded successfully!")
