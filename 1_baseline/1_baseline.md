# RESULTS

## OUTPUT FOR `python train_and_evaluate.py`

```text
1. Loading dataset...
Training on 187 movies, testing on 47 movies.

Training Linear Regression (Baseline)...

================ Linear Regression (Baseline) ================
MAE  (Mean Absolute Error):        $18,801,550.48
RMSE (Root Mean Squared Error):   $27,395,895.37
R²   (Coefficient of Determination): -0.2490

Training Ridge Regression (Regularized)...
/home/student/WBench/M0008/tku-ml-movies/.venv/lib/python3.15/site-packages/sklearn/linear_model/_ridge.py:266: UserWarning: Singular matrix in solving dual problem. Using least-squares solution instead.
  warnings.warn(

================ Ridge Regression (Regularized) ================
MAE  (Mean Absolute Error):        $24,141,595.43
RMSE (Root Mean Squared Error):   $46,167,988.80
R²   (Coefficient of Determination): -2.5471

Training Lasso Regression (Regularized)...

================ Lasso Regression (Regularized) ================
MAE  (Mean Absolute Error):        $16,108,565.43
RMSE (Root Mean Squared Error):   $24,434,581.09
R²   (Coefficient of Determination): 0.0064

Training Random Forest Regressor...

================ Random Forest Regressor ================
MAE  (Mean Absolute Error):        $9,130,999.16
RMSE (Root Mean Squared Error):   $16,831,759.78
R²   (Coefficient of Determination): 0.5285

Training Gradient Boosting Regressor...

================ Gradient Boosting Regressor ================
MAE  (Mean Absolute Error):        $9,667,548.96
RMSE (Root Mean Squared Error):   $17,035,731.82
R²   (Coefficient of Determination): 0.5170

Training XGBoost Regressor...

================ XGBoost Regressor ================
MAE  (Mean Absolute Error):        $15,934,418.00
RMSE (Root Mean Squared Error):   $33,539,366.62
R²   (Coefficient of Determination): -0.8720
```

## OUTPUT FOR `python predict_unreleased.py`

```text
1. Loading historical dataset for production training...
2. Training all production models  (Linear, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost)...
/home/student/WBench/M0008/tku-ml-movies/.venv/lib/python3.15/site-packages/sklearn/linear_model/_ridge.py:266: UserWarning: Singular matrix in solving dual problem. Using least-squares solution instead.
  warnings.warn(
/home/student/WBench/M0008/tku-ml-movies/.venv/lib/python3.15/site-packages/sklearn/linear_model/_coordinate_descent.py:842: ConvergenceWarning: Objective did not converge. You might want to increase the number of iterations, check the scale of the features or consider increasing regularisation. Duality gap: 9.449918e+13, tolerance: 7.773e+13
  model = cd_fast.enet_coordinate_descent(
3. Loading unreleased movies dataset...

4. Generating revenue predictions for unreleased movies across all models:

🎬 Movie: The Hunger Games: Sunrise on the Reaping
   • Linear Regression (Baseline)    : $118,804,150.71
   • Ridge Regression                : $54,871,168.01
   • Lasso Regression                : $110,516,976.69
   • Random Forest                   : $110,481,166.86
   • Gradient Boosting               : $112,846,702.41
   • XGBoost                         : $80,424,048.00
----------------------------------------------------------------------
🎬 Movie: Avengers: Doomsday
   • Linear Regression (Baseline)    : $173,747,789.40
   • Ridge Regression                : $11,507,240.02
   • Lasso Regression                : $158,546,969.99
   • Random Forest                   : $111,167,970.44
   • Gradient Boosting               : $112,846,702.41
   • XGBoost                         : $80,424,048.00
----------------------------------------------------------------------
🎬 Movie: Dune: Part Three
   • Linear Regression (Baseline)    : $142,633,646.71
   • Ridge Regression                : $25,756,264.15
   • Lasso Regression                : $132,319,178.00
   • Random Forest                   : $110,771,000.73
   • Gradient Boosting               : $110,785,032.71
   • XGBoost                         : $75,670,288.00
----------------------------------------------------------------------
🎬 Movie: The Beekeeper 2
   • Linear Regression (Baseline)    : $77,015,818.14
   • Ridge Regression                : $43,554,813.32
   • Lasso Regression                : $57,463,600.47
   • Random Forest                   : $128,077,784.14
   • Gradient Boosting               : $135,903,711.65
   • XGBoost                         : $150,248,640.00
----------------------------------------------------------------------
🎬 Movie: Animal Friends
   • Linear Regression (Baseline)    : $74,965,523.53
   • Ridge Regression                : $32,774,154.84
   • Lasso Regression                : $61,641,583.95
   • Random Forest                   : $83,382,270.47
   • Gradient Boosting               : $77,445,410.72
   • XGBoost                         : $67,163,944.00
----------------------------------------------------------------------
🎬 Movie: Godzilla x Kong: Supernova
   • Linear Regression (Baseline)    : $128,349,182.10
   • Ridge Regression                : $20,789,081.00
   • Lasso Regression                : $114,068,074.26
   • Random Forest                   : $110,560,579.44
   • Gradient Boosting               : $115,279,405.88
   • XGBoost                         : $80,565,200.00
----------------------------------------------------------------------
🎬 Movie: A Quiet Place Part III
   • Linear Regression (Baseline)    : $80,810,127.76
   • Ridge Regression                : $65,648,585.72
   • Lasso Regression                : $90,105,483.39
   • Random Forest                   : $143,283,818.33
   • Gradient Boosting               : $147,859,059.09
   • XGBoost                         : $162,772,848.00
----------------------------------------------------------------------
🎬 Movie: The Legend of Zelda
   • Linear Regression (Baseline)    : $122,536,844.66
   • Ridge Regression                : $36,319,151.47
   • Lasso Regression                : $112,327,590.94
   • Random Forest                   : $110,571,920.78
   • Gradient Boosting               : $115,279,405.88
   • XGBoost                         : $86,271,632.00
----------------------------------------------------------------------
```
