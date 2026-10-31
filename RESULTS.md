# RESULTS

## OUTPUT FOR `python train_and_evaluate.py`

```text
1. Loading dataset...
Training on 400 movies, testing on 100 movies.

Training Linear Regression (Baseline)...

================ Linear Regression (Baseline) ================
MAE  (Mean Absolute Error):        $68,547,014.46
RMSE (Root Mean Squared Error):   $99,173,587.49
R²   (Coefficient of Determination): 0.5252

Training Ridge Regression (Regularized)...
/home/student/WBench/M0008/tku-ml-movies/.venv/lib/python3.15/site-packages/sklearn/linear_model/_ridge.py:227: LinAlgWarning: An ill-conditioned matrix detected: slice 0 has rcond = 4.551825777134564e-19.
  return linalg.solve(A, Xy, assume_a="pos", overwrite_a=True).T

================ Ridge Regression (Regularized) ================
MAE  (Mean Absolute Error):        $48,195,219.35
RMSE (Root Mean Squared Error):   $62,037,553.29
R²   (Coefficient of Determination): 0.8142

Training Lasso Regression (Regularized)...

================ Lasso Regression (Regularized) ================
MAE  (Mean Absolute Error):        $48,126,965.20
RMSE (Root Mean Squared Error):   $61,887,110.43
R²   (Coefficient of Determination): 0.8151

Training Random Forest Regressor...

================ Random Forest Regressor ================
MAE  (Mean Absolute Error):        $35,041,178.29
RMSE (Root Mean Squared Error):   $49,439,651.68
R²   (Coefficient of Determination): 0.8820

Training Gradient Boosting Regressor...

================ Gradient Boosting Regressor ================
MAE  (Mean Absolute Error):        $32,606,632.96
RMSE (Root Mean Squared Error):   $46,036,007.52
R²   (Coefficient of Determination): 0.8977

Training XGBoost Regressor...

================ XGBoost Regressor ================
MAE  (Mean Absolute Error):        $35,330,192.00
RMSE (Root Mean Squared Error):   $48,054,869.71
R²   (Coefficient of Determination): 0.8885
```

## OUTPUT FOR `python predict_unreleased.py`

```text
1. Loading historical dataset for production training...
2. Training all production models (Linear, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost)...
/home/student/WBench/M0008/tku-ml-movies/.venv/lib/python3.15/site-packages/sklearn/linear_model/_ridge.py:227: LinAlgWarning: An ill-conditioned matrix detected: slice 0 has rcond = 4.334536065396191e-19.
  return linalg.solve(A, Xy, assume_a="pos", overwrite_a=True).T
3. Loading unreleased movies dataset...

4. Generating revenue predictions for unreleased movies across all models:

🎬 Movie: Starlight Odyssey
   • Linear Regression (Baseline)    : $270,361,409.83
   • Ridge Regression                : $187,290,078.02
   • Lasso Regression                : $186,326,619.40
   • Random Forest                   : $163,523,915.09
   • Gradient Boosting               : $165,009,729.48
   • XGBoost                         : $178,369,040.00
----------------------------------------------------------------------
🎬 Movie: The Comedy Heist
   • Linear Regression (Baseline)    : $47,692,894.93
   • Ridge Regression                : $42,562,623.31
   • Lasso Regression                : $43,510,432.93
   • Random Forest                   : $42,655,122.99
   • Gradient Boosting               : $44,492,771.60
   • XGBoost                         : $55,563,676.00
----------------------------------------------------------------------
```
