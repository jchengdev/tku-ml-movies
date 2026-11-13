import os

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from train_and_evaluate import preprocess_inference_data, preprocess_training_data
from xgboost import XGBRegressor


def main():
    print("1. Loading historical dataset for production training...")
    if not os.path.exists("movie_box_office_dataset.csv"):
        print("Error: 'movie_box_office_dataset.csv' not found.")
        return

    df = pd.read_csv("movie_box_office_dataset.csv")
    df = preprocess_training_data(df)

    drop_cols = [
        "title",
        "movie_id",
        "release_date",
        "days_since_release",
        "domestic",
        "international",
        "opening",
        "metacritic_score",
        "box_office",
    ]

    X_train = df.drop(columns=[col for col in drop_cols if col in df.columns])
    y_train = df["box_office"]

    # One-hot encode training data
    X_train = pd.get_dummies(X_train, drop_first=True)

    # 2. Train all production models on 100% of mature historical data
    print(
        "2. Training all production models  (Linear, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost)..."
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
        return

    target_movies = pd.read_csv("unreleased_movies.csv")

    # Preprocess unreleased data first
    target_movies = preprocess_inference_data(target_movies)

    # Extract titles AFTER preprocessing and reset index so they match row-for-row
    movie_titles = target_movies["title"].reset_index(drop=True)

    # Drop leakage/identifier columns
    X_unreleased = target_movies.drop(
        columns=[col for col in drop_cols if col in target_movies.columns]
    )

    # One-hot encode, align columns with training feature matrix, and reset index
    X_unreleased = pd.get_dummies(X_unreleased, drop_first=True)
    X_unreleased = X_unreleased.reindex(
        columns=X_train.columns, fill_value=0
    ).reset_index(drop=True)

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
