"""
Box office prediction pipeline (replaces the 6-model / mock-data setup).

Usage:
    python box_office_model.py 3_Months_Box_Office_Data.xlsx [output.xlsx]

Reads the 'Box Office Mojo' sheet (training data) and the 'Unreleased' sheet
(custom / unreleased movies), trains models, evaluates them, and writes a
workbook with the dataset (+ Days Out counter), predictions and metrics.

Only information known BEFORE release is used as a feature. Metacritic score,
domestic/international split, opening and box office are never fed to the model
(they are post-release or are the targets).
"""
import re
import sys
import warnings

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
SEED = 42
TODAY = pd.Timestamp("2026-11-01")          # "today"; Oct 31 => Days Out = 1... see days_out()
HORIZONS = [7, 30, 60, 90]                   # days after release to forecast cumulative box office
MAJORS = ["Disney", "Warner", "Universal", "Paramount", "Sony", "Lionsgate", "20th", "Amazon", "Apple", "Netflix"]
EVENT = ["Fathom", "Trafalgar", "Iconic Events", "GKIDS"]       # event-cinema / re-release distributors
GENRES = ["Drama", "Thriller", "Comedy", "Action", "Documentary", "Adventure",
          "Fantasy", "Horror", "Animation", "Family", "Sci-Fi", "Music"]


# ----------------------------------------------------------------- 1. load & clean
def money(v):
    s = str(v).replace("$", "").replace(",", "").strip()
    return float(s) if re.fullmatch(r"[\d.]+", s) else np.nan


def yes(v):
    return int(str(v).strip().lower() in ("yes", "1", "true"))


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalise either the historical sheet or the 'Unreleased' sheet to one schema."""
    c = {k.lower().strip(): k for k in raw.columns}
    g = lambda *names: next((raw[c[n]] for n in names if n in c), pd.Series(np.nan, index=raw.index))
    df = pd.DataFrame({
        "release": pd.to_datetime(g("release date", "release_date")),
        "title": g("title").astype(str).str.strip(),
        "theaters": pd.to_numeric(g("theaters"), errors="coerce"),
        "duration": pd.to_numeric(g("duration (min)", "duration_minutes"), errors="coerce"),
        "budget": g("budget (usd)", "budget").map(money),
        "rerelease": g("re-release", "re_release").map(yes),
        "sequel": g("sequel/prequel/remake", "sequel_prequel_remake").map(yes),
        "rating": g("rating").astype(str).str.strip().replace({"-": "NR", "M": "NR", "nan": "NR"}),
        "country": g("country").astype(str),
        "genre": g("genre").astype(str),
        "distributor": g("distributor").astype(str).str.strip(),
        "opening": g("opening (usd)", "opening").map(money),
        "box_office": g("box office (usd)", "box_office").map(money),
    })
    df.loc[df.duration > 240, "duration"] = np.nan      # e.g. 'It Ends' has 340 min (copy of its theater count)
    return df


def days_out(release):
    """Days since release, counting Nov 1 (today) - release date: Oct 31 -> 1, Oct 30 -> 2 ..."""
    return (TODAY - release).dt.days


# ----------------------------------------------------------------- outliers
def flag_outliers(df: pd.DataFrame) -> pd.Series:
    """Reason string per film ('' = keep). Rules use 1.5 x IQR on the log10 scale:
    1) box office or opening is extreme on its own;
    2) the worldwide box-office / US-opening ratio is extreme (a mostly-international hit or
       a tiny US release with a huge foreign gross) - not predictable from the pre-release features."""
    def iqr_mask(v):
        l = np.log10(v.where(v > 0))
        q1, q3 = l.quantile([.25, .75])
        k = 1.5 * (q3 - q1)
        return (l < q1 - k) | (l > q3 + k)
    r1 = iqr_mask(df.box_office) | iqr_mask(df.opening)
    r2 = iqr_mask(df.box_office / df.opening)
    reason = pd.Series("", index=df.index)
    reason[r1] = "Extreme opening/box office (1.5xIQR, log scale)"
    reason[r2] = "Box office far out of line with US opening (1.5xIQR on ratio, log scale)"
    reason[r1 & r2] = "Both: extreme value and extreme box office/opening ratio"
    return reason


# ----------------------------------------------------------------- 2. features
def features(df: pd.DataFrame, budget_median: float) -> pd.DataFrame:
    X = pd.DataFrame(index=df.index)
    X["log_theaters"] = np.log1p(df.theaters.fillna(0))
    X["theaters_missing"] = df.theaters.isna().astype(int)
    X["duration"] = df.duration.fillna(106)
    X["log_budget"] = np.log10(df.budget.fillna(budget_median))
    X["budget_missing"] = df.budget.isna().astype(int)
    X["rerelease"], X["sequel"] = df.rerelease, df.sequel
    X["us_production"] = df.country.str.contains("US").astype(int)
    X["major_studio"] = df.distributor.str.contains("|".join(MAJORS)).astype(int)
    X["event_cinema"] = df.distributor.str.contains("|".join(EVENT)).astype(int)
    for r in ["G", "PG", "PG-13", "R"]:
        X["rating_" + r] = (df.rating == r).astype(int)
    for gname in GENRES:
        X["genre_" + gname] = df.genre.str.contains(gname).astype(int)
    return X


def models():
    return {
        "Ridge (baseline)": make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-1, 3, 20))),
        "Random Forest": RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=SEED),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=3,
                                                       subsample=0.8, random_state=SEED),
    }


def metrics(y_log, p_log):
    y, p = 10 ** y_log, 10 ** p_log
    return {"R2 (log scale)": r2_score(y_log, p_log),
            "RMSLE": float(np.sqrt(np.mean((y_log - p_log) ** 2))),
            "Median abs % error": float(np.median(np.abs(p - y) / y)),
            "MAE (USD)": mean_absolute_error(y, p)}


def cv_permutation_importance(model_factory, X, y_log, repeats=5):
    """Permutation importance averaged over 5 CV folds: how much held-out R2 (log scale)
    drops when one feature is shuffled. Comparable across all model types.
    Negative / ~0 = the feature adds nothing (or is noise)."""
    from sklearn.inspection import permutation_importance
    out = []
    for tr, te in KFold(5, shuffle=True, random_state=SEED).split(X):
        m = model_factory().fit(X.iloc[tr], y_log.iloc[tr])
        r = permutation_importance(m, X.iloc[te], y_log.iloc[te], n_repeats=repeats,
                                   random_state=SEED, scoring="r2")
        out.append(r.importances_mean)
    return pd.Series(np.mean(out, axis=0), index=X.columns)


def all_importances(X, y_log):
    cols = {name: cv_permutation_importance(lambda n=name: models()[n], X, y_log) for name in models()}
    df = pd.DataFrame(cols)
    df["Average"] = df.mean(axis=1)
    return df.sort_values("Average", ascending=False)


# ----------------------------------------------------------------- 3. train / evaluate
def evaluate(X, y_log, label, rows):
    Xtr, Xte, ytr, yte = train_test_split(X, y_log, test_size=0.2, random_state=SEED)
    kf = KFold(5, shuffle=True, random_state=SEED)
    print(f"\n=== {label}: {len(Xtr)} train / {len(Xte)} test ===")
    for name, m in models().items():
        test = metrics(yte, m.fit(Xtr, ytr).predict(Xte))
        cv = metrics(y_log, cross_val_predict(m, X, y_log, cv=kf))
        rows.append({"Target": label, "Model": name, "Train n": len(Xtr), "Test n": len(Xte),
                     **{"Test " + k: v for k, v in test.items()}, **{"CV " + k: v for k, v in cv.items()}})
        print(f"{name:18s} test R2={test['R2 (log scale)']:.2f}  CV R2={cv['R2 (log scale)']:.2f}  "
              f"CV median error={cv['Median abs % error']:.0%}")


def main(path, out):
    import os
    if not os.path.exists(path):                       # also look next to this script
        alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(path))
        if os.path.exists(alt):
            path = alt
        else:
            sys.exit(f"Input file not found: {path}\nPut the .xlsx next to this script or pass its full path.")
    hist = clean(pd.read_excel(path, sheet_name="Box Office Mojo"))
    hist["days_out"] = days_out(hist.release)
    hist["outlier"] = flag_outliers(hist)
    print(f"Outliers flagged: {(hist.outlier != '').sum()} of {len(hist)}")
    custom = clean(pd.read_excel(path, sheet_name="Unreleased"))
    bmed = hist.budget.median()

    X = features(hist, bmed)
    X["days_out"] = hist.days_out                      # lets the model learn how totals grow with run length
    m_open = hist.opening.notna() & (hist.opening > 0)
    X_open = X.drop(columns="days_out")[m_open]
    y_open = np.log10(hist.opening[m_open])
    y_box = np.log10(hist.box_office)

    rows = []
    evaluate(X_open, y_open, "Opening", rows)
    evaluate(X, y_box, "Box office to date (days_out as a feature)", rows)
    results = pd.DataFrame(rows)

    # same models / split / CV, but on the films that are not flagged as outliers
    keep = (hist.outlier == "")
    rows_no = []
    print(f"\n##### Repeating evaluation WITHOUT outliers ({int(keep.sum())} films) #####")
    evaluate(X_open[keep[m_open]], y_open[keep[m_open]], "Opening", rows_no)
    evaluate(X[keep], y_box[keep], "Box office to date (days_out as a feature)", rows_no)
    results_no = pd.DataFrame(rows_no)

    # ---- final models: Random Forest (best CV), refit on 100% of the data
    rf_open = models()["Random Forest"].fit(X_open, y_open)
    rf_box = models()["Random Forest"].fit(X, y_box)
    ridge_box = models()["Ridge (baseline)"].fit(X, y_box)
    print("\nComputing permutation importances for all models...")
    imp = {"Opening": all_importances(X_open, y_open),
           "Box office": all_importances(X, y_box)}

    # ---- predict custom movies
    Xc = features(custom, bmed)
    pred = pd.DataFrame({"title": custom.title, "release": custom.release})
    pred["opening"] = 10 ** rf_open.predict(Xc)
    for h in HORIZONS:
        Xh = Xc.assign(days_out=h)
        pred[f"day{h}"] = 10 ** rf_box.predict(Xh)
        pred[f"ridge_day{h}"] = 10 ** ridge_box.predict(Xh)
    # sanity: totals can't shrink over time and can't be below the opening
    cols = [f"day{h}" for h in HORIZONS]
    pred[cols] = np.maximum.accumulate(pred[cols].values, axis=1)
    pred[cols] = np.maximum(pred[cols].values, pred[["opening"]].values)
    print("\n", pred[["title", "opening", "day90", "ridge_day90"]].round(-4).to_string(index=False))

    write_workbook(out, hist, custom, pred, results, results_no, imp, len(hist), int(m_open.sum()))
    print("\nWrote", out)


# ----------------------------------------------------------------- 4. workbook
HDR = PatternFill("solid", fgColor="1F3864")
INP = PatternFill("solid", fgColor="FFF2CC")
F = lambda **k: Font(**{"name": "Arial", "size": 10, **k})


def header(ws, cols, row=1):
    for j, c in enumerate(cols, 1):
        cell = ws.cell(row, j, c)
        cell.font, cell.fill = F(bold=True, color="FFFFFF"), HDR
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def widths(ws, w):
    for j, x in enumerate(w, 1):
        ws.column_dimensions[get_column_letter(j)].width = x


def write_dataset(wb, name, hist, reason=False):
    ws = wb.create_sheet(name)
    cols = ["Release Date", "Title", "Days Out", "Theaters", "Duration (min)", "Budget (USD)", "Re-release",
            "Sequel/Prequel/Remake", "Rating", "Country", "Genre", "Distributor", "Opening Weekend (USD)",
            "Box Office to Date (USD)"]
    if reason:
        cols = cols + ["Outlier Reason"]
    header(ws, cols)
    for i, r in enumerate(hist.itertuples(), 2):
        vals = [r.release.to_pydatetime(), r.title, f"='Read Me'!$B$4-A{i}",
                None if pd.isna(r.theaters) else r.theaters, None if pd.isna(r.duration) else r.duration,
                None if pd.isna(r.budget) else r.budget, "Yes" if r.rerelease else "No",
                "Yes" if r.sequel else "No", r.rating, r.country, r.genre, r.distributor,
                None if pd.isna(r.opening) else r.opening, r.box_office]
        if reason:
            vals = vals + [r.outlier]
        for j, v in enumerate(vals, 1):
            c = ws.cell(i, j, v)
            c.font = F()
        ws.cell(i, 1).number_format = "yyyy-mm-dd"
        ws.cell(i, 3).number_format = "0"
        for j in (4, 5):
            ws.cell(i, j).number_format = "#,##0"
        for j in (6, 13, 14):
            ws.cell(i, j).number_format = "$#,##0"
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(hist) + 1}"
    widths(ws, [12, 34, 9, 10, 10, 15, 10, 12, 8, 12, 36, 26, 16, 18, 60])


def write_metrics(wb, name, results, title):
    ws = wb.create_sheet(name)
    ws["A1"] = f"Evaluation on: {title}"
    ws["A1"].font = F(bold=True)
    mcols = list(results.columns)
    header(ws, mcols, row=2)
    for i, r in enumerate(results.itertuples(index=False), 3):
        for j, v in enumerate(r, 1):
            c = ws.cell(i, j, v)
            c.font = F()
            nm = mcols[j - 1]
            if "R2" in nm or "RMSLE" in nm:
                c.number_format = "0.00"
            elif "%" in nm:
                c.number_format = "0%"
            elif "MAE" in nm:
                c.number_format = "$#,##0"
    widths(ws, [44, 18, 9, 9, 14, 12, 14, 14, 12, 12, 14, 12, 14, 14])


def write_workbook(out, hist, custom, pred, results, results_no, imp, n_train, n_open):
    wb = Workbook()

    # Read Me
    ws = wb.active
    ws.title = "Read Me"
    ws["A1"] = "Box office prediction project"
    ws["A1"].font = F(bold=True, size=14)
    ws["A3"], ws["B3"] = "Assumption", "Value"
    ws["A4"], ws["B4"] = "Today (Days Out = Today - Release Date)", TODAY.to_pydatetime()
    ws["B4"].number_format = "yyyy-mm-dd"
    ws["B4"].fill = INP
    notes = [
        "Days Out counter: Data collected on Nov 1, so a movie released Oct 31 has Days Out = 1, Oct 30 = 2, ... Aug 2 = 91. Change B4 to re-base it.",
        f"Dataset sheet: {n_train} movies released Aug 2 - Oct 30, 2026 (Box Office Mojo). Opening is available for {n_open}; the rest were reported as '-'.",
        "Dataset (No Outliers) / Outliers Removed: films flagged by 1.5xIQR rules (see reason column) are split out. Model Metrics (No Outliers) repeats the evaluation without them; the production model and Predictions still use the full Dataset.",
        "Pre-release features (model inputs; release date/season is deliberately NOT used): theaters, duration, budget, re-release, sequel, rating, country, genre, distributor type.",
        "Excluded as leakage / targets: Metacritic, Domestic %, International %, Opening, Box Office.",
        "'Opening' on Box Office Mojo is the opening WEEKEND (Fri-Sun, domestic), not a single night. The dataset has no opening-night figure.",
        "'Box Office' is cumulative gross to Nov 1 (worldwide), so Days Out is a model feature. Predictions set Days Out to 7/30/60/90.",
        "Custom Movies sheet: edit/add rows (yellow), re-run box_office_model.py to refresh Predictions.",
    ]
    for i, t in enumerate(notes, 6):
        ws.cell(i, 1, t).font = F()
    for c in ("A3", "B3"):
        ws[c].font = F(bold=True)
    ws["A4"].font = F()
    ws["B4"].font = F(color="0000FF")
    widths(ws, [60, 16])

    # Dataset sheets
    write_dataset(wb, "Dataset", hist)
    keep = hist[hist.outlier == ""]
    write_dataset(wb, "Dataset (No Outliers)", keep)
    out_df = hist[hist.outlier != ""]
    write_dataset(wb, "Outliers Removed", out_df, reason=True)

    # Custom Movies (inputs)
    ws = wb.create_sheet("Custom Movies")
    ccols = ["Release Date", "Title", "Theaters", "Duration (min)", "Budget (USD)", "Re-release",
             "Sequel/Prequel/Remake", "Rating", "Country", "Genre", "Distributor"]
    header(ws, ccols)
    for i, r in enumerate(custom.itertuples(), 2):
        vals = [r.release.to_pydatetime(), r.title, r.theaters, r.duration, r.budget,
                "Yes" if r.rerelease else "No", "Yes" if r.sequel else "No", r.rating, r.country, r.genre, r.distributor]
        for j, v in enumerate(vals, 1):
            c = ws.cell(i, j, None if (isinstance(v, float) and np.isnan(v)) else v)
            c.font, c.fill = F(color="0000FF"), INP
        ws.cell(i, 1).number_format = "yyyy-mm-dd"
        ws.cell(i, 5).number_format = "$#,##0"
    widths(ws, [12, 34, 10, 10, 15, 10, 12, 8, 10, 36, 20])

    # Predictions
    ws = wb.create_sheet("Predictions")
    pcols = ["Release Date", "Title", "Opening Weekend (USD)"] + [f"Box Office by Day {h} (USD)" for h in HORIZONS] + \
            ["Ridge cross-check: Day 90 (USD)"]
    header(ws, pcols)
    for i, r in pred.reset_index(drop=True).iterrows():
        vals = [r.release.to_pydatetime(), r.title, r.opening] + [r[f"day{h}"] for h in HORIZONS] + [r["ridge_day90"]]
        for j, v in enumerate(vals, 1):
            c = ws.cell(i + 2, j, v)
            c.font = F()
            if j > 2:
                c.number_format = "$#,##0"
        ws.cell(i + 2, 1).number_format = "yyyy-mm-dd"
    n = len(pred) + 3
    for k, t in enumerate([
        "Primary model: Random Forest (log-scale target). Ridge column is an independent linear cross-check; large gaps = low confidence.",
        "Training films top out at ~4,160 theaters and ~$410M, so blockbuster forecasts (Avengers, Dune, etc.) are the least reliable.",
        "Typical error on held-out movies is large (see Model Metrics): use these as order-of-magnitude estimates."]):
        ws.cell(n + k, 1, t).font = F(italic=True)
    ws.freeze_panes = "C2"
    widths(ws, [12, 34, 20, 20, 20, 20, 20, 24])

    write_metrics(wb, "Model Metrics", results, f"ALL {n_train} films (outliers included)")
    write_metrics(wb, "Model Metrics (No Outliers)", results_no,
                  f"{int((hist.outlier == '').sum())} films (the 10 flagged outliers removed - see 'Outliers Removed')")

    # Feature Importance sheet: every feature, every model, sorted high -> low
    ws = wb.create_sheet("Feature Importance")
    ws["A1"] = ("Permutation importance = drop in held-out R2 (log scale) when the feature is shuffled, averaged over 5 CV folds. "
                "Top rows = most important; bottom rows = least (negative = noise, model does slightly better without it).")
    ws["A1"].font = F(italic=True)
    r = 3
    for target, df in imp.items():
        ws.cell(r, 1, f"{target} model").font = F(bold=True, size=12)
        header(ws, ["Rank", "Feature"] + list(df.columns), row=r + 1)
        for k, (feat, row) in enumerate(df.iterrows(), 1):
            ws.cell(r + 1 + k, 1, k).font = F()
            ws.cell(r + 1 + k, 2, feat).font = F()
            for jj, v in enumerate(row, 3):
                c = ws.cell(r + 1 + k, jj, float(v))
                c.number_format, c.font = "0.000", F()
        n = len(df)
        for jj in range(1, 3 + df.shape[1]):               # shade top 5 green, bottom 5 red
            for k in range(1, 6):
                ws.cell(r + 1 + k, jj).fill = PatternFill("solid", fgColor="E2EFDA")
                ws.cell(r + 1 + n - k + 1, jj).fill = PatternFill("solid", fgColor="FCE4D6")
        r += n + 4
    widths(ws, [8, 22, 16, 16, 18, 12])
    wb.save(out)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "3_Months_Box_Office_Data.xlsx"
    dst = sys.argv[2] if len(sys.argv) > 2 else "Box_Office_Dataset_and_Predictions.xlsx"
    main(src, dst)
