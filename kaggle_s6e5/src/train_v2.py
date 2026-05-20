import lightgbm as lgb
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


def train_v2():
    print("Loading V2 data...")
    train = pd.read_parquet("kaggle_s6e5/data/train_v2.parquet")
    test = pd.read_parquet("kaggle_s6e5/data/test_v2.parquet")

    features = [
        c for col in [train.columns] for c in col if c not in ["id", "PitNextLap"]
    ]
    target = "PitNextLap"

    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

    oof_preds_lgb = np.zeros(len(train))
    oof_preds_cat = np.zeros(len(train))
    test_preds_lgb = np.zeros(len(test))
    test_preds_cat = np.zeros(len(test))

    lgb_params = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "boosting_type": "gbdt",
        "random_state": 42,
        "learning_rate": 0.03,
        "num_leaves": 63,
        "feature_fraction": 0.7,
        "bagging_fraction": 0.7,
        "bagging_freq": 5,
        "n_jobs": -1,
    }

    cat_params = {
        "loss_function": "Logloss",
        "eval_metric": "AUC",
        "random_seed": 42,
        "learning_rate": 0.03,
        "iterations": 1000,
        "depth": 6,
        "l2_leaf_reg": 3,
        "verbose": False,
        "task_type": "CPU",  # Change to GPU if available
    }

    for fold, (train_idx, val_idx) in enumerate(skf.split(train, train[target])):
        print(f"\n--- Fold {fold + 1} ---")
        X_train, y_train = (
            train.iloc[train_idx][features],
            train.iloc[train_idx][target],
        )
        X_val, y_val = train.iloc[val_idx][features], train.iloc[val_idx][target]

        # LGBM
        print("Training LGBM...")
        model_lgb = lgb.LGBMClassifier(**lgb_params, n_estimators=2000)
        model_lgb.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[
                lgb.early_stopping(stopping_rounds=100),
                lgb.log_evaluation(200),
            ],
        )
        oof_preds_lgb[val_idx] = model_lgb.predict_proba(X_val)[:, 1]
        test_preds_lgb += model_lgb.predict_proba(test[features])[:, 1] / skf.n_splits

        # CatBoost
        print("Training CatBoost...")
        model_cat = CatBoostClassifier(**cat_params)
        model_cat.fit(
            X_train, y_train, eval_set=(X_val, y_val), early_stopping_rounds=100
        )
        oof_preds_cat[val_idx] = model_cat.predict_proba(X_val)[:, 1]
        test_preds_cat += model_cat.predict_proba(test[features])[:, 1] / skf.n_splits

    auc_lgb = roc_auc_score(train[target], oof_preds_lgb)
    auc_cat = roc_auc_score(train[target], oof_preds_cat)

    # Weighted Blend
    # I'll optimize weights later, for now 50/50
    final_oof = 0.5 * oof_preds_lgb + 0.5 * oof_preds_cat
    auc_blend = roc_auc_score(train[target], final_oof)

    print(f"\nLGBM OOF AUC: {auc_lgb:.5f}")
    print(f"Cat OOF AUC: {auc_cat:.5f}")
    print(f"Blend OOF AUC: {auc_blend:.5f}")

    # Save submission
    final_test = 0.5 * test_preds_lgb + 0.5 * test_preds_cat
    sub = pd.DataFrame({"id": test["id"], "PitNextLap": final_test})
    sub.to_csv("kaggle_s6e5/submissions/sub_v2_ensemble.csv", index=False)
    print("V2 ensemble submission saved. 🥒")


if __name__ == "__main__":
    train_v2()
