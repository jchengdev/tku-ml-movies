import os

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from xgboost import XGBRegressor


def main():
    print("1. Loading historical dataset for production training...")
    if not os.path.exists("movie_box_office_dataset.csv"):
        print(
            "Error: 'movie_box_office_dataset.csv' not found. Please ensure your dataset is in the project folder."
        )
        return

    df = pd.read_csv("movie_box_office_dataset.csv")

    # Separate features and target from historical data
    X_train = df.drop(columns=["movie_id", "title", "box_office_revenue_usd"])
    y_train = df["box_office_revenue_usd"]

    # One-hot encode training data
    X_train = pd.get_dummies(X_train, drop_first=True)

    # 2. Train all production models on 100% of historical data
    print(
        "2. Training all production models (Linear, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost)..."
    )
    models = {
        "Linear Regression (Baseline)": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0, random_state=42),
        "Lasso Regression": Lasso(alpha=100.0, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42, learning_rate=0.1),
    }

    for model in models.values():
        model.fit(X_train, y_train)

    print("3. Loading unreleased movies dataset...")
    if not os.path.exists("unreleased_movies.csv"):
        print("Error: 'unreleased_movies.csv' not found.")
        print(
            "Please ensure your unreleased movies CSV is present in the project folder."
        )
        return

    target_movies = pd.read_csv("unreleased_movies.csv")
    movie_titles = target_movies["title"]

    # Preprocess and align columns
    X_unreleased = target_movies.drop(columns=["movie_id", "title"])
    X_unreleased = pd.get_dummies(X_unreleased, drop_first=True)
    X_unreleased = X_unreleased.reindex(columns=X_train.columns, fill_value=0)

    # 4. Generate Predictions from each model
    print(
        "\n4. Generating revenue predictions for unreleased movies across all models:\n"
    )

    for idx, title in enumerate(movie_titles):
        print(f"🎬 Movie: {title}")
        single_movie = X_unreleased.iloc[[idx]]

        for name, model in models.items():
            pred = model.predict(single_movie)[0]
            print(f"   • {name:<32}: ${pred:,.2f}")
        print("-" * 70)


if __name__ == "__main__":
    main()
