# RESULTS

## OUTPUT FOR `python train_and_evaluate.py`

```text
1. Loading dataset...
📊 [Maturity Filter] Evaluated 234 total historical records.
   • Filtered out 49 rows released less than 30 days prior to 2026-11-12 (preventing truncation bias).
   • Retained 185 mature records for model training.

Training on 148 movies, testing on 37 movies.

Training Linear Regression (Baseline)...

================ Linear Regression (Baseline) ================
MAE  (Mean Absolute Error):        $23,762,500.26
RMSE (Root Mean Squared Error):   $61,702,893.14
R²   (Coefficient of Determination): 0.3042

Training Ridge Regression (Regularized)...
/home/student/WBench/M0008/tku-ml-movies/.venv/lib/python3.15/site-packages/sklearn/linear_model/_ridge.py:266: UserWarning: Singular matrix in solving dual problem. Using least-squares solution instead.
  warnings.warn(

================ Ridge Regression (Regularized) ================
MAE  (Mean Absolute Error):        $22,867,866.04
RMSE (Root Mean Squared Error):   $61,277,196.90
R²   (Coefficient of Determination): 0.3138

Training Lasso Regression (Regularized)...

================ Lasso Regression (Regularized) ================
MAE  (Mean Absolute Error):        $21,864,306.76
RMSE (Root Mean Squared Error):   $60,568,903.84
R²   (Coefficient of Determination): 0.3295

Training Random Forest Regressor...

================ Random Forest Regressor ================
MAE  (Mean Absolute Error):        $14,311,040.84
RMSE (Root Mean Squared Error):   $48,861,122.73
R²   (Coefficient of Determination): 0.5637

Training Gradient Boosting Regressor...

================ Gradient Boosting Regressor ================
MAE  (Mean Absolute Error):        $15,617,032.84
RMSE (Root Mean Squared Error):   $47,615,849.92
R²   (Coefficient of Determination): 0.5856

Training XGBoost Regressor...

================ XGBoost Regressor ================
MAE  (Mean Absolute Error):        $14,536,047.00
RMSE (Root Mean Squared Error):   $45,278,358.61
R²   (Coefficient of Determination): 0.6253
```

## OUTPUT FOR `python predict_unreleased.py`

```text
1. Loading historical dataset for production training...
📊 [Maturity Filter] Evaluated 234 total historical records.
   • Filtered out 49 rows released less than 30 days prior to 2026-11-12 (preventing truncation bias).
   • Retained 185 mature records for model training.

2. Training all production models  (Linear, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost)...
/home/student/WBench/M0008/tku-ml-movies/.venv/lib/python3.15/site-packages/sklearn/linear_model/_ridge.py:266: UserWarning: Singular matrix in solving dual problem. Using least-squares solution instead.
  warnings.warn(
3. Loading unreleased movies dataset...

4. Generating revenue predictions for unreleased movies across all models:

🎬 Movie: The Hunger Games: Sunrise on the Reaping
   • Linear Regression (Baseline)    : $118,261,280.73
   • Ridge Regression                : $110,603,320.62
   • Lasso Regression                : $116,926,583.05
   • Random Forest                   : $120,198,873.34
   • Gradient Boosting               : $142,773,273.92
   • XGBoost                         : $122,239,688.00
----------------------------------------------------------------------
🎬 Movie: Avengers: Doomsday
   • Linear Regression (Baseline)    : $166,142,982.32
   • Ridge Regression                : $139,880,342.57
   • Lasso Regression                : $160,524,774.07
   • Random Forest                   : $121,127,647.25
   • Gradient Boosting               : $142,773,273.92
   • XGBoost                         : $122,239,688.00
----------------------------------------------------------------------
🎬 Movie: Dune: Part Three
   • Linear Regression (Baseline)    : $137,760,156.95
   • Ridge Regression                : $121,282,412.91
   • Lasso Regression                : $132,300,870.85
   • Random Forest                   : $116,434,777.21
   • Gradient Boosting               : $138,189,809.83
   • XGBoost                         : $102,415,080.00
----------------------------------------------------------------------
🎬 Movie: The Beekeeper 2
   • Linear Regression (Baseline)    : $80,112,763.55
   • Ridge Regression                : $70,589,665.97
   • Lasso Regression                : $70,960,373.12
   • Random Forest                   : $150,991,522.08
   • Gradient Boosting               : $150,500,370.70
   • XGBoost                         : $169,774,528.00
----------------------------------------------------------------------
🎬 Movie: Animal Friends
   • Linear Regression (Baseline)    : $76,953,925.02
   • Ridge Regression                : $67,081,046.22
   • Lasso Regression                : $63,504,074.69
   • Random Forest                   : $77,982,847.32
   • Gradient Boosting               : $41,181,249.64
   • XGBoost                         : $69,254,024.00
----------------------------------------------------------------------
🎬 Movie: Godzilla x Kong: Supernova
   • Linear Regression (Baseline)    : $125,900,230.89
   • Ridge Regression                : $102,963,957.55
   • Lasso Regression                : $114,157,717.53
   • Random Forest                   : $115,022,248.33
   • Gradient Boosting               : $126,760,347.66
   • XGBoost                         : $102,349,640.00
----------------------------------------------------------------------
🎬 Movie: A Quiet Place Part III
   • Linear Regression (Baseline)    : $83,790,986.86
   • Ridge Regression                : $83,668,915.76
   • Lasso Regression                : $85,587,276.07
   • Random Forest                   : $154,605,244.81
   • Gradient Boosting               : $158,290,133.75
   • XGBoost                         : $173,731,408.00
----------------------------------------------------------------------
🎬 Movie: The Legend of Zelda
   • Linear Regression (Baseline)    : $121,411,177.83
   • Ridge Regression                : $103,754,368.89
   • Lasso Regression                : $116,115,381.41
   • Random Forest                   : $118,217,718.06
   • Gradient Boosting               : $131,099,272.38
   • XGBoost                         : $122,228,088.00
----------------------------------------------------------------------
```
