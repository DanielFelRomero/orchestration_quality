import mlcroissant as mlc
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")


def preparar_lotes() -> None:
    print("Descargando el dataset de referencia...")
    dataset = mlc.Dataset(
        "https://www.kaggle.com/datasets/shivamb/netflix-shows/croissant/download"
    )

    record_sets = dataset.metadata.record_sets
    df = pd.DataFrame(dataset.records(record_set=record_sets[0].uuid))

    df.columns = [
        column.replace("netflix_titles.csv/", "")
        for column in df.columns
    ]

    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].apply(
                lambda value: value.decode("utf-8")
                if isinstance(value, bytes)
                else value
            )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    lote_bueno = df.head(500).copy()
    lote_bueno.to_csv(
        DATA_DIR / "lote_dia_1_bueno.csv",
        index=False,
    )

    lote_malo = df.tail(500).copy()

    lote_malo.loc[lote_malo.index[0], "release_year"] = 3026
    lote_malo.loc[lote_malo.index[1], "type"] = "Podcast"
    lote_malo.loc[lote_malo.index[2], "show_id"] = None

    lote_malo.to_csv(
        DATA_DIR / "lote_dia_2_malo.csv",
        index=False,
    )

    print("Lotes preparados en data/raw/")
    print(" - lote_dia_1_bueno.csv")
    print(" - lote_dia_2_malo.csv")


if __name__ == "__main__":
    preparar_lotes()
