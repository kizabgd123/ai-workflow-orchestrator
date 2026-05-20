import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold


def oof_target_encode(train, test, col, target="PitNextLap"):
    print(f"Target encoding {col}...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    train[f"{col}_target_enc"] = 0.0
    test[f"{col}_target_enc"] = 0.0

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


def oof_expected_pit_life(train, test, target="PitNextLap"):
    print("Calculating expected pit tyre life...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    train["Expected_Pit_TyreLife"] = 0.0
    test["Expected_Pit_TyreLife"] = 0.0

    for train_idx, val_idx in skf.split(train, train[target]):
        # Calculate mean tyre life where PitNextLap == 1 grouped by Race and Compound on train folds
        train_fold = train.iloc[train_idx]
        pit_stops = train_fold[train_fold[target] == 1]
        mean_life = pit_stops.groupby(["Race", "Compound"])["TyreLife"].mean()
        # Apply to validation fold
        train.loc[val_idx, "Expected_Pit_TyreLife"] = (
            train.loc[val_idx].set_index(["Race", "Compound"]).index.map(mean_life)
        )

    # Apply to test using full train
    full_pit_stops = train[train[target] == 1]
    full_mean_life = full_pit_stops.groupby(["Race", "Compound"])["TyreLife"].mean()
    test["Expected_Pit_TyreLife"] = test.set_index(["Race", "Compound"]).index.map(
        full_mean_life
    )

    # Fill missing values:
    # First, fallback to compound-level expected pit life:
    compound_mean = full_pit_stops.groupby("Compound")["TyreLife"].mean()
    train["Expected_Pit_TyreLife"] = train["Expected_Pit_TyreLife"].fillna(
        train["Compound"].map(compound_mean)
    )
    test["Expected_Pit_TyreLife"] = test["Expected_Pit_TyreLife"].fillna(
        test["Compound"].map(compound_mean)
    )

    # Second, fallback to global mean tyre life at pit stop:
    global_pit_mean = full_pit_stops["TyreLife"].mean()
    train["Expected_Pit_TyreLife"] = train["Expected_Pit_TyreLife"].fillna(
        global_pit_mean
    )
    test["Expected_Pit_TyreLife"] = test["Expected_Pit_TyreLife"].fillna(
        global_pit_mean
    )

    return train, test


def engineer_features_v4():
    train = pd.read_parquet("kaggle_s6e5/data/train_proc.parquet")
    test = pd.read_parquet("kaggle_s6e5/data/test_proc.parquet")

    # Target encode important categoricals
    for col in ["Race", "Compound", "Driver"]:
        train, test = oof_target_encode(train, test, col)

    # Expected pit tyre life
    train, test = oof_expected_pit_life(train, test)

    # Feature engineering
    print("Creating advanced features (V4)...")
    for df in [train, test]:
        # Tyre logic
        df["TyreLife_Sq"] = df["TyreLife"] ** 2
        df["RaceProgress_Sq"] = df["RaceProgress"] ** 2
        df["LapNumber_per_Stint"] = df["LapNumber"] / (df["Stint"] + 1e-6)

        # Risk factor: TyreLife high at end of race
        df["End_Race_Risk"] = df["TyreLife"] * df["RaceProgress"]

        # Expected pit tyre life features
        df["TyreLife_vs_Expected"] = df["TyreLife"] / (
            df["Expected_Pit_TyreLife"] + 1e-6
        )
        df["TyreLife_Remaining_Expected"] = df["Expected_Pit_TyreLife"] - df["TyreLife"]
        df["TyreLife_Over_Expected"] = (
            df["TyreLife"] - df["Expected_Pit_TyreLife"]
        ).clip(lower=0)

        # LapTime Normalization
        df["Mean_LapTime_Race_Year"] = df.groupby(["Race", "Year"])[
            "LapTime (s)"
        ].transform("mean")
        df["LapTime_Diff_Race_Year"] = df["LapTime (s)"] - df["Mean_LapTime_Race_Year"]
        df["LapTime_Ratio_Race_Year"] = df["LapTime (s)"] / (
            df["Mean_LapTime_Race_Year"] + 1e-6
        )

        # --- NEW ELITE F1 FEATURES ---
        # 1. Race-Lap average lap time (captures safety car / VSC track-wide slow downs)
        df["Race_Lap_Mean_LapTime"] = df.groupby(["Race", "Year", "LapNumber"])[
            "LapTime (s)"
        ].transform("mean")
        # 2. Safety car indicator (lap average is > 15% slower than race/year average)
        df["SafetyCar_Indicator"] = (
            df["Race_Lap_Mean_LapTime"] / (df["Mean_LapTime_Race_Year"] + 1e-6) > 1.15
        ).astype(int)
        # 3. LapTime deficit relative to the fastest car on that lap
        df["LapTime_Diff_Min_Lap"] = df["LapTime (s)"] - df.groupby(
            ["Race", "Year", "LapNumber"]
        )["LapTime (s)"].transform("min")
        # 4. Driver's pace percentile rank on that lap (captures relative speed/traffic position)
        df["Driver_Pace_Rank"] = df.groupby(["Race", "Year", "LapNumber"])[
            "LapTime (s)"
        ].rank(pct=True)
        # -----------------------------

        # Degradation Rate
        df["Degradation_Rate"] = df["Cumulative_Degradation"] / (df["TyreLife"] + 1e-6)
        df["Degradation_vs_Progress"] = (
            df["Cumulative_Degradation"] * df["RaceProgress"]
        )

        # Stint Progress
        df["Stint_Lap_Ratio"] = df["TyreLife"] / (df["LapNumber"] + 1e-6)

        # Position gain / change
        df["Position_Change_Sq"] = df["Position_Change"] ** 2
        df["LapTime_Delta_Sq"] = df["LapTime_Delta"] ** 2

    train.to_parquet("kaggle_s6e5/data/train_v4.parquet", index=False)
    test.to_parquet("kaggle_s6e5/data/test_v4.parquet", index=False)
    print("V4 features ready! 🥒🚀")


if __name__ == "__main__":
    engineer_features_v4()
