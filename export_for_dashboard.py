import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

os.makedirs("dashboard_data", exist_ok=True)

exports = {
    "top_games": """
        SELECT g.name, r.positive_ratio, r.total_reviews,
               p.price, p.is_free
        FROM games g
        JOIN reviews_summary r ON g.app_id = r.app_id
        JOIN prices p ON g.app_id = p.app_id
        ORDER BY r.positive_ratio DESC
    """,
    "genre_summary": """
        SELECT ge.genre_name,
               COUNT(DISTINCT g.app_id) as num_games,
               ROUND(AVG(r.positive_ratio),1) as avg_positive_pct,
               ROUND(AVG(p.price),2) as avg_price,
               SUM(r.total_reviews) as total_reviews
        FROM genres ge
        JOIN game_genres gg ON ge.genre_id = gg.genre_id
        JOIN games g ON gg.app_id = g.app_id
        JOIN reviews_summary r ON g.app_id = r.app_id
        JOIN prices p ON g.app_id = p.app_id
        GROUP BY ge.genre_name
    """,
    "price_tiers": """
        SELECT CASE
            WHEN p.price = 0 THEN 'Free'
            WHEN p.price < 5 THEN 'Budget (<$5)'
            WHEN p.price < 15 THEN 'Indie ($5-$15)'
            WHEN p.price < 30 THEN 'Mid ($15-$30)'
            ELSE 'Premium ($30+)'
        END as tier,
        COUNT(*) as num_games,
        ROUND(AVG(r.positive_ratio),1) as avg_positive_pct
        FROM prices p
        JOIN reviews_summary r ON p.app_id = r.app_id
        GROUP BY tier
    """,
    "developer_leaderboard": """
        SELECT d.developer_name,
               COUNT(g.app_id) as num_games,
               ROUND(AVG(r.positive_ratio),1) as avg_positive_pct,
               ROUND(AVG(p.price),2) as avg_price,
               SUM(r.total_reviews) as total_reviews
        FROM developers d
        JOIN games g ON d.developer_id = g.developer_id
        JOIN reviews_summary r ON g.app_id = r.app_id
        JOIN prices p ON g.app_id = p.app_id
        GROUP BY d.developer_name
        HAVING COUNT(g.app_id) >= 2
        ORDER BY avg_positive_pct DESC
    """
}

for name, query in exports.items():
    df = pd.read_sql(query, engine)
    df.to_csv(f"dashboard_data/{name}.csv", index=False)
    print(f"Exported {name}.csv — {len(df)} rows")

print("\n✅ All exports done!")
