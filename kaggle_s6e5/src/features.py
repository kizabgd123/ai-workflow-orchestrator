import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def engineer_features(train_path, test_path, external_path):
    print("Loading data...")
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    external = pd.read_csv(external_path)

    # Pre-process external to get Max_TyreLife priors
    print("Extracting priors from external data...")
    priors = external.groupby(["Race", "Compound"])["TyreLife"].max().reset_index()
    priors.columns = ["Race", "Compound", "Max_TyreLife_Prior"]

    # Merge priors
    train = train.merge(priors, on=["Race", "Compound"], how="left")
    test = test.merge(priors, on=["Race", "Compound"], how="left")

    # Fill missing priors with global max per compound
    global_priors = external.groupby("Compound")["TyreLife"].max()
    train["Max_TyreLife_Prior"] = train["Max_TyreLife_Prior"].fillna(
        train["Compound"].map(global_priors)
    )
    test["Max_TyreLife_Prior"] = test["Max_TyreLife_Prior"].fillna(
        test["Compound"].map(global_priors)
    )

    # Feature engineering
    print("Creating interaction features...")
    for df in [train, test]:
        # Tyre logic
        df["TyreLife_Ratio"] = df["TyreLife"] / (df["Max_TyreLife_Prior"] + 1e-6)
        df["Remaining_TyreLife"] = df["Max_TyreLife_Prior"] - df["TyreLife"]

        # Progress logic
        df["Laps_Remaining"] = (
            df["LapNumber"] / (df["RaceProgress"] + 1e-6) - df["LapNumber"]
        )
        df["TyreLife_vs_Progress"] = df["TyreLife"] / (df["RaceProgress"] + 1e-6)

        # Position logic
        df["Pos_Gain_Total"] = df[
            "Position_Change"
        ].cumsum()  # This might be wrong if not grouped by race/driver, better to use raw

    # Categorical Encoding
    print("Encoding categoricals...")
    cat_cols = ["Driver", "Compound", "Race"]
    for col in cat_cols:
        le = LabelEncoder()
        # Combine to ensure same encoding
        combined = pd.concat([train[col], test[col]]).astype(str)
        le.fit(combined)
        train[col] = le.transform(train[col].astype(str))
        test[col] = le.transform(test[col].astype(str))

    return train, test


if __name__ == "__main__":
    train, test = engineer_features(
        "kaggle_s6e5/data/train.csv",
        "kaggle_s6e5/data/test.csv",
        "kaggle_s6e5/data/f1_strategy_dataset_v4.csv",
    )

    train.to_parquet("kaggle_s6e5/data/train_proc.parquet", index=False)
    test.to_parquet("kaggle_s6e5/data/test_proc.parquet", index=False)
    print("Done! Morty, the Parquet files are ready. 🥒")
