# Movie box office prediction

Run: `python box_office_model.py 3_Months_Box_Office_Data.xlsx` (needs pandas, numpy, scikit-learn, openpyxl).
Output: `Box_Office_Dataset_and_Predictions.xlsx` (Read Me, Dataset with Days Out, Custom Movies, Predictions, Model Metrics).
To predict your own movies, edit the yellow rows on the `Unreleased` sheet of the input file (same columns) and re-run.

## 1. Data collection
234 real films released Aug 2 - Oct 30, 2026 (Box Office Mojo), in the `Box Office Mojo` sheet. Days Out = Nov 1 minus release date
(Oct 31 = 1). Only pre-release fields are features: theaters, duration, budget, re-release, sequel, rating,
country, genre, distributor type. Metacritic and Domestic/International % are post-release and are excluded.

## 2. Dataset preparation and split
- Money strings (`$1,234`, `-`) become numbers; `-` becomes missing. Duration > 240 min set to missing (typo, e.g. "It Ends" = 340).
- Missing theaters/budget: median/zero fill plus a "was missing" flag (70% of budgets are missing, mostly small/foreign films).
- Targets are log10-transformed (box office spans $205 to $410M).
- Genres multi-hot, rating one-hot, distributor flagged as major studio / event cinema. Directors and production companies
  are dropped (almost no repeats in 234 films, so they only add noise).
- 80/20 random split (seed 42), plus 5-fold cross-validation because 47 test films is a small sample.
  Final models are refit on all data for predictions.

## 3. Models
Ridge (baseline), Random Forest, Gradient Boosting. Random Forest was chosen: best CV score on both targets,
handles the non-linear theater/budget effects and mixed binary features, and needs little tuning with ~200 rows.
Parameters: 300 trees, min_samples_leaf=2, seed 42. Ridge alpha is chosen by internal CV.
Two models: opening weekend (features only), and cumulative box office (features + Days Out). A 7/30/60/90-day forecast
is the second model with Days Out set to that value.

## 4. Evaluation
R2 and RMSLE on the log scale, median absolute % error, and MAE in USD, on the held-out test set and in 5-fold CV.

| Target | Model | Test R2 (log) | CV R2 (log) | CV median % error |
|---|---|---|---|---|
| Opening | Random Forest | 0.78 | 0.84 | 52% |
| Box office | Random Forest | 0.35 | 0.56 | 86% |

## 5. Insights and limits
See the `Feature Importance` sheet (permutation importance for all 3 models, every feature ranked, top 5 green / bottom 5 red). Theater count dominates (~65% of importance), then duration (~13%), Days Out (~6%) and budget (~3%). Sequel and major-studio flags matter little once theaters are known (they mostly act through the theater count).
The model deliberately ignores release date/season; it only uses the movie's own factors and Days Out.
Limits: opening is the opening weekend, not a single night; training has few blockbusters (max ~4,160 theaters, ~$410M),
so Avengers/Dune/Hunger Games-scale forecasts are badly under-predicted by the forest and over-predicted by the Ridge
cross-check; treat the two as a rough range.
