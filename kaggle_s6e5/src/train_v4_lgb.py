import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold


def train_v4_lgb():
    print("Loading V4 data...")
    train = pd.read_parquet(
        "ai-workflow-orchestrator/kaggle_s6e5/data/train_v4.parquet"
    )
    test = pd.read_parquet("ai-workflow-orchestrator/kaggle_s6e5/data/test_v4.parquet")

    features = [c for c in train.columns if c not in ["id", "PitNextLap"]]
    target = "PitNextLap"

    print(f"Features ({len(features)}): {features}")

    # 5-Fold Stratified CV (Enough for calibration)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    oof_preds = np.zeros(len(train))
    test_preds = np.zeros(len(test))

    lgb_params = {
        "objective": "binary",
        "metric": "none",  # Using custom metric instead
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

    for fold, (train_idx, val_idx) in enumerate(skf.split(train, train[target])):
        print(f"\n--- Fold {fold + 1} ---")
        X_train, y_train = (
            train.iloc[train_idx][features],
            train.iloc[train_idx][target],
        )
        X_val, y_val = train.iloc[val_idx][features], train.iloc[val_idx][target]

        # LGBM with Custom F1-Macro metric
        print("Training LGBM with F1-Macro optimization...")
        model_lgb = lgb.LGBMClassifier(**lgb_params, n_estimators=2500)
        model_lgb.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            eval_metric=f1_macro_lgbm_eval,
            callbacks=[
                lgb.early_stopping(stopping_rounds=100),
                lgb.log_evaluation(500),
            ],
        )

        # Calibration Step (Phase 3 of dr-custom-metrics)
        print("Calibrating probabilities using Isotonic Regression...")
        calibrated_model = CalibratedClassifierCV(
            model_lgb, method="isotonic", cv="prefit"
        )
        calibrated_model.fit(X_val, y_val)

        oof_preds[val_idx] = calibrated_model.predict_proba(X_val)[:, 1]
        test_preds += (
            calibrated_model.predict_proba(test[features])[:, 1] / skf.n_splits
        )

        fold_auc = roc_auc_score(y_val, oof_preds[val_idx])
        fold_f1 = f1_score(
            y_val, (oof_preds[val_idx] > 0.5).astype(int), average="macro"
        )
        print(f"Fold {fold + 1} LGBM - AUC: {fold_auc:.5f} | F1-Macro: {fold_f1:.5f}")

    auc_total = roc_auc_score(train[target], oof_preds)
    f1_total = f1_score(train[target], (oof_preds > 0.5).astype(int), average="macro")
    print("\n=============================")
    print(f"LGBM V4 OOF AUC: {auc_total:.5f}")
    print(f"LGBM V4 OOF F1-Macro: {f1_total:.5f}")
    print("=============================")

    # Save submission
    sub = pd.DataFrame({"id": test["id"], "PitNextLap": test_preds})
    os.makedirs("ai-workflow-orchestrator/kaggle_s6e5/submissions", exist_ok=True)
    sub.to_csv(
        "ai-workflow-orchestrator/kaggle_s6e5/submissions/sub_v4_calibrated.csv",
        index=False,
    )
    print("V4 Calibrated LightGBM submission saved successfully! 🥒🚀")


if __name__ == "__main__":
    train_v4_lgb()
