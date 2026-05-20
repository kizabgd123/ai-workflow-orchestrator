import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


def train_v3():
    print("Loading V3 data...")
    train = pd.read_parquet("kaggle_s6e5/data/train_v3.parquet")
    test = pd.read_parquet("kaggle_s6e5/data/test_v3.parquet")

    features = [c for c in train.columns if c not in ["id", "PitNextLap"]]
    target = "PitNextLap"

    print(f"Features ({len(features)}): {features}")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    oof_preds_lgb = np.zeros(len(train))
    test_preds_lgb = np.zeros(len(test))

    lgb_params = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "boosting_type": "gbdt",
        "random_state": 42,
        "learning_rate": 0.05,
        "num_leaves": 127,
        "max_depth": 8,
        "min_child_samples": 30,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "n_jobs": -1,
    }

    fold_scores = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(train, train[target])):
        print(f"\n--- Fold {fold + 1} ---")
        X_train, y_train = (
            train.iloc[train_idx][features],
            train.iloc[train_idx][target],
        )
        X_val, y_val = train.iloc[val_idx][features], train.iloc[val_idx][target]

        # LGBM
        print("Training LGBM...")
        model_lgb = lgb.LGBMClassifier(**lgb_params, n_estimators=3000)
        model_lgb.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[
                lgb.early_stopping(stopping_rounds=100, verbose=False),
                lgb.log_evaluation(500),
            ],
        )

        val_preds = model_lgb.predict_proba(X_val)[:, 1]
        oof_preds_lgb[val_idx] = val_preds
        test_preds_lgb += model_lgb.predict_proba(test[features])[:, 1] / skf.n_splits

        fold_score = roc_auc_score(y_val, val_preds)
        fold_scores.append(fold_score)
        print(f"Fold {fold + 1} LGBM AUC: {fold_score:.5f}")

    auc_lgb = roc_auc_score(train[target], oof_preds_lgb)
    print(f"\n=============================")
    print(f"LGBM OOF AUC: {auc_lgb:.5f}")
    print(f"CV Mean: {np.mean(fold_scores):.5f} ± {np.std(fold_scores):.5f}")
    print(f"=============================")

    # Save submission
    os.makedirs("kaggle_s6e5/submissions", exist_ok=True)
    sub = pd.DataFrame({"id": test["id"], "PitNextLap": test_preds_lgb})
    sub.to_csv("kaggle_s6e5/submissions/sub_v3_lgb.csv", index=False)
    print("V3 LGBM submission saved. 🥒🚀")


if __name__ == "__main__":
    train_v3()
