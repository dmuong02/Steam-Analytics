-- 1. Top 10 games by positive review ratio
SELECT g.name, rs.positive_ratio
FROM games g
JOIN reviews_summary rs ON g.app_id = rs.app_id
ORDER BY rs.positive_ratio DESC
LIMIT 10;

-- 2. Average price by genre
SELECT gen.genre_name, AVG(p.price) as average_price
FROM genres gen
JOIN game_genres gg ON gen.genre_id = gg.genre_id
JOIN prices p ON gg.app_id = p.app_id
GROUP BY gen.genre_name;

-- 3. Price Tier Analysis
SELECT 
    CASE 
        WHEN p.price = 0 THEN '1. Free'
        WHEN p.price < 5 THEN '2. Budget (<$5)'
        WHEN p.price < 15 THEN '3. Low-cost ($5-$15)'
        WHEN p.price < 30 THEN '4. Mid ($15-$30)'
        ELSE '5. Premium ($30+)'
    END AS price_tier,
    COUNT(*) AS num_games,
    ROUND(AVG(r.positive_ratio), 1) AS avg_positive_pct,
    ROUND(AVG(g.average_playtime) / 60.0, 1) AS avg_playtime_hours
FROM prices p
JOIN games g ON p.app_id = g.app_id
JOIN reviews_summary r ON g.app_id = r.app_id
GROUP BY price_tier
ORDER BY price_tier;

-- 4. Developer Leaderboard
SELECT 
    d.developer_name,
    COUNT(g.app_id) AS num_games,
    ROUND(AVG(r.positive_ratio), 1) AS avg_positive_pct,
    ROUND(AVG(p.price), 2) AS avg_price,
    SUM(r.total_reviews) AS total_reviews
FROM developers d
JOIN games g ON d.developer_id = g.developer_id
JOIN reviews_summary r ON g.app_id = r.app_id
JOIN prices p ON g.app_id = p.app_id
GROUP BY d.developer_name
HAVING COUNT(g.app_id) >= 2
ORDER BY avg_positive_pct DESC
LIMIT 15;

-- 5. Genre Popularity Ranking With Window Functions
WITH genre_stats AS (
    SELECT 
        ge.genre_name,
        COUNT(DISTINCT g.app_id) AS game_count,
        ROUND(AVG(r.positive_ratio), 1) AS avg_positive_pct,
        SUM(r.total_reviews) AS total_reviews
    FROM genres ge
    JOIN game_genres gg ON ge.genre_id = gg.genre_id
    JOIN games g ON gg.app_id = g.app_id
    JOIN reviews_summary r ON g.app_id = r.app_id
    GROUP BY ge.genre_name
)
SELECT 
    genre_name,
    game_count,
    avg_positive_pct,
    total_reviews,
    RANK() OVER (ORDER BY game_count DESC) AS popularity_rank,
    RANK() OVER (ORDER BY avg_positive_pct DESC) AS sentiment_rank
FROM genre_stats
ORDER BY popularity_rank;

-- 6. Best Value Games (High Positive Reviews, Low Price)
WITH value_score AS (
    SELECT 
        g.name,
        p.price,
        r.positive_ratio,
        r.total_reviews,
        ROUND(r.positive_ratio / NULLIF(p.price, 0), 2) AS value_score
    FROM games g
    JOIN prices p ON g.app_id = p.app_id
    JOIN reviews_summary r ON g.app_id = r.app_id
    WHERE p.price BETWEEN 1 AND 20
    AND r.total_reviews > 500
)
SELECT * FROM value_score
ORDER BY value_score DESC
LIMIT 10;

-- 7. Games Above Their Genre's Average Price (Window Function)
WITH genre_avg AS (
    SELECT 
        g.app_id,
        g.name,
        p.price,
        ge.genre_name,
        ROUND(AVG(p.price) OVER (PARTITION BY ge.genre_id), 2) AS genre_avg_price
    FROM games g
    JOIN prices p ON g.app_id = p.app_id
    JOIN game_genres gg ON g.app_id = gg.app_id
    JOIN genres ge ON gg.genre_id = ge.genre_id
    WHERE p.price > 0
)
SELECT 
    name,
    genre_name,
    price,
    genre_avg_price,
    ROUND(price - genre_avg_price, 2) AS price_premium
FROM genre_avg
WHERE price > genre_avg_price
ORDER BY price_premium DESC
LIMIT 15;

-- 8. Review Sentiment vs Price Correlation
SELECT 
    ROUND(CORR(p.price, r.positive_ratio)::NUMERIC, 3) AS price_sentiment_correlation,
    COUNT(*) AS games_analyzed
FROM prices p
JOIN reviews_summary r ON p.app_id = r.app_id
WHERE p.price > 0;

-- 9. Free vs paid games comparison
SELECT 
    CASE WHEN p.is_free = true THEN 'Free to Play' ELSE 'Paid' END AS model,
    COUNT(*) AS num_games,
    ROUND(AVG(r.positive_ratio), 1) AS avg_positive_pct,
    SUM(r.total_reviews) AS total_reviews,
    ROUND(AVG(r.total_reviews), 0) AS avg_reviews_per_game
FROM prices p
JOIN reviews_summary r ON p.app_id = r.app_id
GROUP BY model
ORDER BY model;

-- 10. Top Genres by Total Player Engagment (Average Playtime)
SELECT 
    ge.genre_name,
    COUNT(DISTINCT g.app_id) AS num_games,
    SUM(r.total_reviews) AS total_reviews,
    ROUND(AVG(r.positive_ratio), 1) AS avg_sentiment,
    ROUND(SUM(r.total_reviews) / COUNT(DISTINCT g.app_id), 0) AS avg_reviews_per_game,
    RANK() OVER (ORDER BY SUM(r.total_reviews) DESC) AS engagement_rank
FROM genres ge
JOIN game_genres gg ON ge.genre_id = gg.genre_id
JOIN games g ON gg.app_id = g.app_id
JOIN reviews_summary r ON g.app_id = r.app_id
GROUP BY ge.genre_name
ORDER BY engagement_rank;
