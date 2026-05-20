import numpy as np
import pandas as pd


def profile_data(file_path):
    print(f"\n--- Profiling {file_path} ---")
    df = pd.read_csv(file_path)
    print(f"Shape: {df.shape}")
    print("\nColumns and Types:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())

    if "PitNextLap" in df.columns:
        print("\nTarget Distribution (PitNextLap):")
        print(df["PitNextLap"].value_counts(normalize=True))

    return df


train_df = profile_data("kaggle_s6e5/data/train.csv")
test_df = profile_data("kaggle_s6e5/data/test.csv")

# Check first few rows
print("\nFirst 5 rows of train:")
print(train_df.head())
