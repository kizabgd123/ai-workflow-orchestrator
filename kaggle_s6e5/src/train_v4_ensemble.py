import lightgbm as lgb
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


def train_v4_ensemble():
    print("Loading V4 data...")
    train = pd.read_parquet("kaggle_s6e5/data/train_v4.parquet")
    test = pd.read_parquet("kaggle_s6e5/data/test_v4.parquet")

    features = [c for c in train.columns if c not in ["id", "PitNextLap"]]
    target = "PitNextLap"

    print(f"Features ({len(features)}): {features}")

    # 10-Fold Stratified CV for ultimate stability and top leaderboard score
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
        "learning_rate": 0.04,
        "num_leaves": 63,
        "max_depth": 6,
        "min_child_samples": 30,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "n_jobs": -1,
    }

    cat_params = {
        "loss_function": "Logloss",
        "eval_metric": "AUC",
        "random_seed": 42,
        "learning_rate": 0.05,
        "iterations": 1200,
        "depth": 6,
        "l2_leaf_reg": 4,
        "verbose": False,
        "task_type": "CPU",
        "thread_count": -1,
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
            callbacks=[lgb.early_stopping(stopping_rounds=100), lgb.log_evaluation(0)],
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

        # Intermediate fold evaluation
        fold_lgb_auc = roc_auc_score(y_val, oof_preds_lgb[val_idx])
        fold_cat_auc = roc_auc_score(y_val, oof_preds_cat[val_idx])
        fold_blend_auc = roc_auc_score(
            y_val, 0.5 * oof_preds_lgb[val_idx] + 0.5 * oof_preds_cat[val_idx]
        )
        print(
            f"Fold {fold + 1} -> LGBM AUC: {fold_lgb_auc:.5f} | CatBoost AUC: {fold_cat_auc:.5f} | Blend AUC: {fold_blend_auc:.5f}"
        )

    auc_lgb = roc_auc_score(train[target], oof_preds_lgb)
    auc_cat = roc_auc_score(train[target], oof_preds_cat)

    # 50/50 blend
    final_oof = 0.5 * oof_preds_lgb + 0.5 * oof_preds_cat
    auc_blend = roc_auc_score(train[target], final_oof)

    print("\n=============================")
    print(f"LGBM OOF AUC: {auc_lgb:.5f}")
    print(f"CatBoost OOF AUC: {auc_cat:.5f}")
    print(f"BLEND OOF AUC: {auc_blend:.5f}")
    print("=============================")

    # Save submission
    final_test = 0.5 * test_preds_lgb + 0.5 * test_preds_cat
    sub = pd.DataFrame({"id": test["id"], "PitNextLap": final_test})
    sub.to_csv("kaggle_s6e5/submissions/sub_v4_ensemble.csv", index=False)
    print("V4 ensemble submission saved successfully! 🥒🚀")


if __name__ == "__main__":
    train_v4_ensemble()
