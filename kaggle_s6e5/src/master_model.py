import glob

import lightgbm as lgb
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder

# --- PATH DISCOVERY ---
print("Scanning /kaggle/input...")
for name in glob.glob("/kaggle/input/**/*", recursive=True):
    print(name)

# --- UPDATED PATHS (Guessed from common patterns) ---
INPUT_DIR = "/kaggle/input/playground-series-s6e5"
EXTERNAL_DIR = "/kaggle/input/f1-strategy-dataset-v4"
OUTPUT_DIR = "/kaggle/working"


def load_and_preprocess():
    print("Loading data...")
    train = pd.read_csv(f"{INPUT_DIR}/train.csv")
    test = pd.read_csv(f"{INPUT_DIR}/test.csv")
    external = pd.read_csv(f"{EXTERNAL_DIR}/f1_strategy_dataset_v4.csv")

    # 1. External Priors (Legal Leak)
    print("Extracting priors...")
    priors = external.groupby(["Race", "Compound"])["TyreLife"].max().reset_index()
    priors.columns = ["Race", "Compound", "Max_TyreLife_Prior"]

    train = train.merge(priors, on=["Race", "Compound"], how="left")
    test = test.merge(priors, on=["Race", "Compound"], how="left")

    global_priors = external.groupby("Compound")["TyreLife"].max()
    train["Max_TyreLife_Prior"] = train["Max_TyreLife_Prior"].fillna(
        train["Compound"].map(global_priors)
    )
    test["Max_TyreLife_Prior"] = test["Max_TyreLife_Prior"].fillna(
        test["Compound"].map(global_priors)
    )

    # 2. Feature Engineering
    print("Engineering features...")
    for df in [train, test]:
        df["TyreLife_Ratio"] = df["TyreLife"] / (df["Max_TyreLife_Prior"] + 1e-6)
        df["Remaining_TyreLife"] = df["Max_TyreLife_Prior"] - df["TyreLife"]
        df["Laps_Remaining"] = (
            df["LapNumber"] / (df["RaceProgress"] + 1e-6) - df["LapNumber"]
        )
        df["TyreLife_vs_Progress"] = df["TyreLife"] / (df["RaceProgress"] + 1e-6)
        df["End_Race_Risk"] = df["TyreLife"] * df["RaceProgress"]
        df["TyreLife_Sq"] = df["TyreLife"] ** 2
        df["LapNumber_per_Stint"] = df["LapNumber"] / (df["Stint"] + 1e-6)

    # 3. Encoding
    cat_cols = ["Driver", "Compound", "Race"]
    for col in cat_cols:
        le = LabelEncoder()
        combined = pd.concat([train[col], test[col]]).astype(str)
        le.fit(combined)
        train[col] = le.transform(train[col].astype(str))
        test[col] = le.transform(test[col].astype(str))

    return train, test


def train_and_submit(train, test):
    features = [c for c in train.columns if c not in ["id", "PitNextLap"]]
    target = "PitNextLap"

    # 10-Fold for maximum stability
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

    oof_lgb = np.zeros(len(train))
    oof_cat = np.zeros(len(train))
    test_lgb = np.zeros(len(test))
    test_cat = np.zeros(len(test))

    lgb_params = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "boosting_type": "gbdt",
        "random_state": 42,
        "learning_rate": 0.02,
        "num_leaves": 127,
        "feature_fraction": 0.6,
        "bagging_fraction": 0.7,
        "bagging_freq": 5,
        "n_jobs": -1,
    }

    cat_params = {
        "loss_function": "Logloss",
        "eval_metric": "AUC",
        "random_seed": 42,
        "learning_rate": 0.02,
        "iterations": 2000,
        "depth": 8,
        "l2_leaf_reg": 5,
        "verbose": 200,
        "task_type": "CPU",
    }

    for fold, (train_idx, val_idx) in enumerate(skf.split(train, train[target])):
        print(f"\n--- Fold {fold + 1} ---")
        X_tr, y_tr = train.iloc[train_idx][features], train.iloc[train_idx][target]
        X_val, y_val = train.iloc[val_idx][features], train.iloc[val_idx][target]

        # LGBM
        m_lgb = lgb.LGBMClassifier(**lgb_params, n_estimators=3000)
        m_lgb.fit(
            X_tr,
            y_tr,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(100), lgb.log_evaluation(500)],
        )
        oof_lgb[val_idx] = m_lgb.predict_proba(X_val)[:, 1]
        test_lgb += m_lgb.predict_proba(test[features])[:, 1] / skf.n_splits

        # CatBoost
        m_cat = CatBoostClassifier(**cat_params)
        m_cat.fit(X_tr, y_tr, eval_set=(X_val, y_val), early_stopping_rounds=100)
        oof_cat[val_idx] = m_cat.predict_proba(X_val)[:, 1]
        test_cat += m_cat.predict_proba(test[features])[:, 1] / skf.n_splits

    # Final Blend
    final_oof = 0.5 * oof_lgb + 0.5 * oof_cat
    print(f"\nENSEMBLE OOF AUC: {roc_auc_score(train[target], final_oof):.5f}")

    final_test = 0.5 * test_lgb + 0.5 * test_cat
    sub = pd.DataFrame({"id": test["id"], "PitNextLap": final_test})
    sub.to_csv("submission.csv", index=False)
    print("Submission generated successfully! 🥒🚀")


if __name__ == "__main__":
    train_df, test_df = load_and_preprocess()
    train_and_submit(train_df, test_df)
