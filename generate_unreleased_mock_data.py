import pandas as pd


def generate_unreleased_mock_data():
    print("Generating mock unreleased movies dataset...")

    unreleased_data = {
        "movie_id": [201, 202],
        "title": ["Starlight Odyssey", "The Comedy Heist"],
        "genre": ["Sci-Fi", "Comedy"],
        "budget_usd": [180000000, 30000000],
        "runtime_minutes": [130, 96],
        "is_sequel_or_prequel": [0, 0],
        "ip_source_type": ["Book", "Original"],
        "distributor_tier": ["Major Studio", "Mid-Tier"],
        "mpaa_rating": ["PG-13", "R"],
        "director_hist_avg_revenue_usd": [350000000, 40000000],
        "lead_actor_hist_avg_revenue_usd": [250000000, 60000000],
        "release_month": [7, 12],
        "is_summer_release": [1, 0],
        "is_holiday_release": [0, 1],
    }

    unreleased_df = pd.DataFrame(unreleased_data)
    unreleased_df.to_csv("unreleased_movies.csv", index=False)
    print("Unreleased mock dataset successfully created: unreleased_movies.csv")


if __name__ == "__main__":
    generate_unreleased_mock_data()
