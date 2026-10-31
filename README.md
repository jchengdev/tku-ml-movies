# Movie Box Office Revenue Prediction - ML Pipeline

This repository contains an end-to-end machine learning pipeline built with Python and `scikit-learn` to predict movie box office revenues using pre-release features (such as production budget, runtime, studio tier, IP type, and director track record).

---

## 1. Environment Setup & Dependencies

Before running any Python scripts, create and activate a local virtual environment (`.venv`) to isolate dependencies, then install the required packages:

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate

# On Windows (Command Prompt / PowerShell):
# .venv\Scripts\activate

# Install required packages
pip install scikit-learn pandas numpy xgboost
```

---

## 2. Execution Guide (Running the ML Pipeline)

Execute the Python scripts sequentially in the following order:

### Step 1: Generate Mock Datasets
Generates the historical training dataset (`movie_box_office_dataset.csv`, 500 rows) and an unreleased target dataset (`unreleased_movies.csv`):
```bash
python generate_mock_data.py
python generate_unreleased_mock_data.py
```

### Step 2: Train and Evaluate Models
Loads the historical dataset, applies One-Hot Encoding (`pd.get_dummies`), performs an 80/20 train/test split, and benchmarks six distinct regression algorithms side-by-side:
* **Linear Regression (Baseline)**
* **Ridge Regression (L2 Regularized)**
* **Lasso Regression (L1 Regularized)**
* **Random Forest Regressor (Ensemble Bagging)**
* **Gradient Boosting Regressor (Ensemble Boosting)**
* **XGBoost Regressor (Advanced Boosting)**

Outputs evaluation metrics for each model including **MAE (Mean Absolute Error)**, **RMSE (Root Mean Squared Error)**, and **$R^2$ (Coefficient of Determination)**.

```bash
python train_and_evaluate.py
```

### Step 3: Run Predictions on Unreleased Movies
Trains production instances of all six models on 100% of the historical dataset, loads `unreleased_movies.csv`, aligns the categorical feature columns (`reindex`), and outputs side-by-side revenue forecasts for upcoming films:

```bash
python predict_unreleased.py
```