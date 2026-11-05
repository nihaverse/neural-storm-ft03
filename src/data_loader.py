import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/raw/train_FD001.txt")

columns = (
    ["engine_id", "cycle"]
    + [f"op_setting_{i}" for i in range(1, 4)]
    + [f"sensor_{i}" for i in range(1, 22)]
)


def load_data():

    df = pd.read_csv(
        DATA_PATH,
        sep=r"\s+",
        header=None,
        names=columns
    )

    return df


if __name__ == "__main__":

    df = load_data()

    print("Dataset shape:", df.shape)
    print("\nFirst five rows:")
    print(df.head())

    print("\nNumber of engines:", df["engine_id"].nunique())

    print("\nMissing values:", df.isnull().sum().sum())