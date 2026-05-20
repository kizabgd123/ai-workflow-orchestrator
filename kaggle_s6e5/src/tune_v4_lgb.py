import lightgbm as lgb
import numpy as np
import pandas as pd
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold


def hyperopt_lgbm_v4():
    print("Loading V4 data for tuning...")
    train = pd.read_parquet("kaggle_s6e5/data/train_v4.parquet")

    features = [c for c in train.columns if c not in ["id", "PitNextLap"]]
    target = "PitNextLap"

    X = train[features]
    y = train[target]

    # Define search space
    space = {
        "max_depth": hp.quniform("max_depth", 4, 12, 1),
        "num_leaves": hp.quniform("num_leaves", 31, 255, 1),
        "learning_rate": hp.loguniform("learning_rate", np.log(0.01), np.log(0.1)),
        "min_child_samples": hp.quniform("min_child_samples", 10, 100, 5),
        "feature_fraction": hp.uniform("feature_fraction", 0.5, 1.0),
        "bagging_fraction": hp.uniform("bagging_fraction", 0.5, 1.0),
        "bagging_freq": hp.quniform("bagging_freq", 1, 10, 1),
        "reg_alpha": hp.loguniform("reg_alpha", np.log(1e-4), np.log(10)),
        "reg_lambda": hp.loguniform("reg_lambda", np.log(1e-4), np.log(10)),
    }

    def objective(params):
        # Cast quniform params to int
        params["max_depth"] = int(params["max_depth"])
        params["num_leaves"] = int(params["num_leaves"])
        params["min_child_samples"] = int(params["min_child_samples"])
        params["bagging_freq"] = int(params["bagging_freq"])

        # Fixed params
        params["objective"] = "binary"
        params["metric"] = "auc"
        params["verbosity"] = -1
        params["boosting_type"] = "gbdt"
        params["random_state"] = 42
        params["n_jobs"] = -1

        # 5-Fold Stratified CV for speed during tuning
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = []

        for train_idx, val_idx in skf.split(X, y):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

            model = lgb.LGBMClassifier(**params, n_estimators=1000)
            model.fit(
                X_tr,
                y_tr,
                eval_set=[(X_val, y_val)],
                callbacks=[
                    lgb.early_stopping(stopping_rounds=50),
                    lgb.log_evaluation(0),
                ],
            )

            preds = model.predict_proba(X_val)[:, 1]
            scores.append(roc_auc_score(y_val, preds))

        return {"loss": -np.mean(scores), "status": STATUS_OK}

    print("Starting Hyperopt optimization (50 evals)...")
    trials = Trials()
    best = fmin(
        fn=objective, space=space, algo=tpe.suggest, max_evals=50, trials=trials
    )

    print(f"\nBest HyperOpt result: AUC = {-trials.best_trial['result']['loss']:.5f}")
    print(f"Best params: {best}")

    # Save best params to a file for later use
    import json

    with open("kaggle_s6e5/src/best_params_lgb_v4.json", "w") as f:
        # Convert any numpy types to python types for json serialization
        serializable_best = {
            k: float(v) if isinstance(v, (np.float32, np.float64, np.int64)) else v
            for k, v in best.items()
        }
        json.dump(serializable_best, f, indent=4)
    print("Best parameters saved to kaggle_s6e5/src/best_params_lgb_v4.json")


if __name__ == "__main__":
    hyperopt_lgbm_v4()
