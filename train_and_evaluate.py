import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


def preprocess_data(df):
    df = df.copy()

    # Clean theater counts
    if "theaters" in df.columns:
        df["theaters"] = pd.to_numeric(
            df["theaters"].astype(str).str.replace(",", "").str.strip(), errors="coerce"
        )
        # Fill missing theaters with the median theater count
        df["theaters"] = df["theaters"].fillna(df["theaters"].median())

    # Fill missing duration with median
    if "duration_minutes" in df.columns:
        df["duration_minutes"] = df["duration_minutes"].fillna(
            df["duration_minutes"].median()
        )

    # Fill missing budget with median (or 0)
    if "budget" in df.columns:
        df["budget"] = df["budget"].fillna(df["budget"].median())

    # Parse release date
    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        df["release_month"] = df["release_date"].dt.month
        df["is_summer_release"] = df["release_month"].isin([5, 6, 7]).astype(int)
        df["is_holiday_release"] = df["release_month"].isin([11, 12]).astype(int)

    return df


def main():
    print("1. Loading dataset...")
    df = pd.read_csv("movie_box_office_dataset.csv")

    df = preprocess_data(df)

    # 2. Define columns to drop (Target, Identifiers, Post-release Leakage)
    drop_cols = [
        "title",
        "movie_id",
        "release_date",
        "domestic",
        "international",
        "opening",
        "metacritic_score",
        "box_office",
    ]

    X = df.drop(columns=[col for col in drop_cols if col in df.columns])
    y = df["box_office"]

    # 3. Handle Categorical Data (One-Hot Encoding)
    X = pd.get_dummies(X, drop_first=True)

    # 4. Train/Test Split (80% training, 20% testing)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training on {len(X_train)} movies, testing on {len(X_test)} movies.\n")

    # Initialize all models
    models = {
        "Linear Regression (Baseline)": LinearRegression(),
        "Ridge Regression (Regularized)": Ridge(alpha=1.0, random_state=42),
        "Lasso Regression (Regularized)": Lasso(alpha=100.0, random_state=42),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=100, random_state=42
        ),
        "Gradient Boosting Regressor": GradientBoostingRegressor(random_state=42),
        "XGBoost Regressor": XGBRegressor(
            n_estimators=100, random_state=42, learning_rate=0.1
        ),
    }

    # Train and evaluate each model
    for model_name, model in models.items():
        print(f"Training {model_name}...")
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)

        print(f"\n================ {model_name} ================")
        print(f"MAE  (Mean Absolute Error):        ${mae:,.2f}")
        print(f"RMSE (Root Mean Squared Error):   ${rmse:,.2f}")
        print(f"R²   (Coefficient of Determination): {r2:.4f}\n")


if __name__ == "__main__":
    main()
