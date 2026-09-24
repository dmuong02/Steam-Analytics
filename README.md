# Steam Market Analytics Dashboard

I built this project to look at the 100 most popular games on Steam and find out how price, genre, and developer relate to how much players like a game. A Python script pulls game data from two Steam APIs and stores it in a PostgreSQL database, and I use SQL and Power BI to analyze it.

**[View the dashboard on Power BI](https://app.powerbi.com/view?r=eyJrIjoiNDk2NWUwZTAtMDM2OC00NWMzLWEyMjUtNGE4NzhiYmU1YTc5IiwidCI6ImY2YjZkZDViLWYwMmYtNDQxYS05OWEwLTE2MmFjNTA2MGJkMiIsImMiOjZ9)**

![Dashboard preview](images/dashboard_overview.png)

## What I Wanted to Find Out

1. Do more expensive games get better reviews?
2. Which genres cost the most, and which get the best reviews?
3. Which developers make consistently well-reviewed games?
4. Do free-to-play games get better or worse reviews than paid games?

## What I Found

To measure how much players like a game, I used its positive review percentage: the share of Steam reviews that recommend it.

- Among paid games, price has almost no connection to review scores. The correlation between them is -0.01, where 0 means no relationship at all.
- Games priced $5 to $15 have the best reviews of any price range, averaging 91.8% positive.
- Paid games average 86.5% positive reviews, compared with 76.2% for free-to-play games.
- Action is the most common genre (78 of the 100 games), but Strategy games have the highest average price at $39.
- Valve has 11 games in the top 100, more than any other developer, and they average 93.6% positive across 11.9 million reviews.

## How It Works

1. **Collect:** `fetch_data.py` pulls data on the top 100 games from the Steam Store API and the SteamSpy API.
2. **Build the database:** `create_tables.py` creates six tables in a Neon PostgreSQL database: `games`, `developers`, `genres`, `game_genres`, `prices`, and `reviews_summary`. Because one game can have several genres, `game_genres` links each game to each of its genres.
3. **Clean and load:** `load_data.py` cleans the data and loads it into those tables.
4. **Analyze:** `analysis.sql` has 10 queries that answer the questions above. They use joins across several tables, CTEs, CASE statements to group games into price ranges, and window functions like RANK() to rank genres.
5. **Visualize:** `export_for_dashboard.py` exports the query results to CSV, and I built a three-page dashboard in Power BI.

## Dashboard Pages

1. **Game Performance Overview:** the top games and how price compares with reviews (shown above).
2. **Genre Analysis:** review scores, game counts, and total reviews for each genre.

![Genre analysis](images/dashboard_genres.png)

3. **Pricing & Developers:** a developer leaderboard and a breakdown by price range.

![Pricing and developers](images/dashboard_pricing.png)

## Limitations

- The data only covers the top 100 games, so the findings describe popular games, not Steam as a whole.
- Review percentages only reflect players who chose to leave a review.
- Some groups are small. For example, the free vs. paid comparison splits 100 games into two groups, so treat those results as a starting point, not a firm conclusion.
- Genre averages count a game once in each of its genres, so a game with several genres shows up in more than one average.
- The data is a snapshot from when I ran the pipeline. Prices and reviews change over time.

## What I Learned

- Pulling data from two APIs and combining it for the same games.
- Designing related tables, including a linking table for games with more than one genre.
- Writing SQL joins across several tables, CTEs, CASE statements, and window functions.
- Building a multi-page Power BI dashboard and publishing it online.

## Tools

Python (pandas, SQLAlchemy) · PostgreSQL (Neon) · SQL · Power BI

## Next Steps

- Pull a larger set of games to see whether these patterns hold beyond the most popular titles.