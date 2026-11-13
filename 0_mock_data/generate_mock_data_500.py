import random

import pandas as pd


def generate_mock_data(num_rows=500):
    print(f"Generating {num_rows} rows of mock movie data...")

    genres = [
        "Sci-Fi",
        "Action",
        "Comedy",
        "Drama",
        "Horror",
        "Fantasy",
        "Romance",
        "Thriller",
    ]
    ip_sources = ["Original", "Book", "Comic / Book", "Remake"]
    distributors = ["Major Studio", "Mid-Tier", "Independent"]
    mpaa_ratings = ["PG", "PG-13", "R"]

    adjectives = [
        "Dark",
        "Last",
        "Hidden",
        "Final",
        "Secret",
        "Lost",
        "Infinite",
        "Wild",
        "Neon",
        "Silent",
    ]
    nouns = [
        "Journey",
        "Empire",
        "Chronicles",
        "Protocol",
        "Escape",
        "Dream",
        "Shadow",
        "Revenge",
        "Horizon",
        "Storm",
    ]

    data = []

    for i in range(1, num_rows + 1):
        movie_id = 1000 + i
        title = f"{random.choice(adjectives)} {random.choice(nouns)} {i if i > 10 else ''}".strip()
        genre = random.choice(genres)

        budget = random.randint(2000000, 250000000)
        runtime = random.randint(85, 170)
        is_sequel = random.choice([0, 0, 0, 1])
        ip_source = random.choice(ip_sources)
        distributor = random.choice(distributors)
        mpaa = random.choice(mpaa_ratings)

        dir_avg = int(budget * random.uniform(0.8, 2.5))
        actor_avg = int(budget * random.uniform(0.7, 2.2))

        release_month = random.randint(1, 12)
        is_summer = 1 if release_month in [5, 6, 7] else 0
        is_holiday = 1 if release_month in [11, 12] else 0

        studio_multiplier = (
            1.8
            if distributor == "Major Studio"
            else (1.2 if distributor == "Mid-Tier" else 0.8)
        )
        sequel_boost = 1.3 if is_sequel == 1 else 1.0
        summer_holiday_boost = 1.15 if (is_summer or is_holiday) else 1.0

        noise = random.uniform(0.7, 1.4)
        box_office = int(
            budget * studio_multiplier * sequel_boost * summer_holiday_boost * noise
        )

        data.append(
            {
                "movie_id": movie_id,
                "title": title,
                "genre": genre,
                "budget_usd": budget,
                "runtime_minutes": runtime,
                "is_sequel_or_prequel": is_sequel,
                "ip_source_type": ip_source,
                "distributor_tier": distributor,
                "mpaa_rating": mpaa,
                "director_hist_avg_revenue_usd": dir_avg,
                "lead_actor_hist_avg_revenue_usd": actor_avg,
                "release_month": release_month,
                "is_summer_release": is_summer,
                "is_holiday_release": is_holiday,
                "box_office_revenue_usd": box_office,
            }
        )

    df = pd.DataFrame(data)
    df.to_csv("movie_box_office_dataset.csv", index=False)
    print("Dataset successfully created: movie_box_office_dataset.csv")


if __name__ == "__main__":
    generate_mock_data()
