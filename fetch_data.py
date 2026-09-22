import requests
import pandas as pd
import time
import json

def get_steamspy_all():
    """Get top 1000 games from SteamSpy"""
    print("Fetching top games from SteamSpy...")
    url = "https://steamspy.com/api.php?request=top100in2weeks"
    response = requests.get(url)
    data = response.json()
    games = list(data.values())
    print(f"Got {len(games)} games from SteamSpy")
    return games

def get_steam_details(appid):
    """Get detailed info for one game from Steam Store API"""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data[str(appid)]["success"]:
            return data[str(appid)]["data"]
    except:
        pass
    return None

# ── Step 1: Get top games list ─────────────────────────────
games = get_steamspy_all()

# ── Step 2: Enrich with Steam Store details ────────────────
print("Fetching details from Steam Store API...")
enriched = []

for i, game in enumerate(games[:100]):  # start with 100 games
    appid = game["appid"]
    details = get_steam_details(appid)
    
    if details:
        game["steam_details"] = details
        enriched.append(game)
        print(f"  [{i+1}/100] {game['name']} ✓")
    else:
        print(f"  [{i+1}/100] {game['name']} — skipped")
    
    time.sleep(1.5)  # be respectful to the API

# ── Step 3: Save raw data ──────────────────────────────────
with open("data/raw_games.json", "w") as f:
    json.dump(enriched, f)

print(f"\n✅ Saved {len(enriched)} games to data/raw_games.json")
