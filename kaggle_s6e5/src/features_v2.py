import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold


def oof_target_encode(train, test, col, target="PitNextLap"):
    print(f"Target encoding {col}...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    train[f"{col}_target_enc"] = 0
    test[f"{col}_target_enc"] = 0

    for train_idx, val_idx in skf.split(train, train[target]):
        # Calculate mean on train folds
        mean_val = train.iloc[train_idx].groupby(col)[target].mean()
        # Apply to validation fold
        train.loc[val_idx, f"{col}_target_enc"] = train.loc[val_idx, col].map(mean_val)

    # Apply to test (using full train)
    full_mean = train.groupby(col)[target].mean()
    test[f"{col}_target_enc"] = test[col].map(full_mean)

    # Fill NAs
    global_mean = train[target].mean()
    train[f"{col}_target_enc"] = train[f"{col}_target_enc"].fillna(global_mean)
    test[f"{col}_target_enc"] = test[f"{col}_target_enc"].fillna(global_mean)

    return train, test


def engineer_features_v2():
    train = pd.read_parquet("kaggle_s6e5/data/train_proc.parquet")
    test = pd.read_parquet("kaggle_s6e5/data/test_proc.parquet")

    # Target encode important categoricals
    for col in ["Race", "Compound", "Driver"]:
        train, test = oof_target_encode(train, test, col)

    # Non-linear features
    print("Adding non-linear features...")
    for df in [train, test]:
        df["TyreLife_Sq"] = df["TyreLife"] ** 2
        df["RaceProgress_Sq"] = df["RaceProgress"] ** 2
        df["LapNumber_per_Stint"] = df["LapNumber"] / (df["Stint"] + 1e-6)

        # Risk factor: TyreLife high at end of race
        df["End_Race_Risk"] = df["TyreLife"] * df["RaceProgress"]

    # Grouped aggregates (Aggregating within each Race + Driver combo)
    # This might be tricky without full group info, but let's try some simple ones
    # LapTime stability
    # df['LapTime_Mean'] = ...

    train.to_parquet("kaggle_s6e5/data/train_v2.parquet", index=False)
    test.to_parquet("kaggle_s6e5/data/test_v2.parquet", index=False)
    print("V2 features ready. 🥒")


if __name__ == "__main__":
    engineer_features_v2()
