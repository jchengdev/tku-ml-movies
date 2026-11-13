import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


def main():
    print("1. Loading dataset...")
    df = pd.read_csv("movie_box_office_dataset.csv")

    # 2. Separate Features (X) and Target (y)
    X = df.drop(columns=["movie_id", "title", "box_office_revenue_usd"])
    y = df["box_office_revenue_usd"]

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
