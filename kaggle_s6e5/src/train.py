import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


def train_lgb():
    print("Loading processed data...")
    train = pd.read_parquet("kaggle_s6e5/data/train_proc.parquet")
    test = pd.read_parquet("kaggle_s6e5/data/test_proc.parquet")

    features = [
        c for col in [train.columns] for c in col if c not in ["id", "PitNextLap"]
    ]
    target = "PitNextLap"

    print(f"Features ({len(features)}): {features}")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    oof_preds = np.zeros(len(train))
    test_preds = np.zeros(len(test))

    params = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "boosting_type": "gbdt",
        "random_state": 42,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "n_jobs": -1,
    }

    for fold, (train_idx, val_idx) in enumerate(skf.split(train, train[target])):
        print(f"\n--- Fold {fold + 1} ---")
        X_train, y_train = (
            train.iloc[train_idx][features],
            train.iloc[train_idx][target],
        )
        X_val, y_val = train.iloc[val_idx][features], train.iloc[val_idx][target]

        model = lgb.LGBMClassifier(**params, n_estimators=1000)
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(100)],
        )

        oof_preds[val_idx] = model.predict_proba(X_val)[:, 1]
        test_preds += model.predict_proba(test[features])[:, 1] / skf.n_splits

    auc = roc_auc_score(train[target], oof_preds)
    print(f"\nOOF AUC: {auc:.5f}")

    # Save submission
    sub = pd.DataFrame({"id": test["id"], "PitNextLap": test_preds})
    sub.to_csv("kaggle_s6e5/submissions/sub_lgb_baseline.csv", index=False)
    print("Baseline submission saved. 🥒")


if __name__ == "__main__":
    train_lgb()
