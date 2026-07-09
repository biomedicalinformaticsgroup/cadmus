"""Migration script: convert existing retrieved_df.json.zip -> Parquet articles table

Usage:
    python scripts/migrate_retrieved_df_to_parquet.py
"""
import zipfile
import json
import os
import shutil
import pandas as pd
from cadmus.storage import Storage


def load_retrieved_df(zip_path="./output/retrieved_df/retrieved_df.json.zip"):
    if not os.path.exists(zip_path):
        raise FileNotFoundError(zip_path)
    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        if "retrieved_df.json" not in names:
            raise ValueError("retrieved_df.json not found inside zip")
        with z.open("retrieved_df.json") as f:
            data = json.load(f)
    # stored as orient='index' in original code
    df = pd.DataFrame.from_dict(data, orient="index")
    return df


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    # basic normalization: ensure identifier columns exist and pub_date is datetime
    df = df.copy()
    for col in ["doi", "pmid", "pmcid", "title", "journal"]:
        if col not in df.columns:
            df[col] = None
    if "pub_date" in df.columns:
        try:
            df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")
        except Exception:
            df["pub_date"] = pd.NaT
    else:
        df["pub_date"] = pd.NaT
    # authors, project_tags, provenance may be dicts; convert to JSON strings
    for col in ["authors", "project_tags", "provenance"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: json.dumps(x) if not pd.isna(x) else None)
        else:
            df[col] = None
    return df


def main():
    zip_path = "./output/retrieved_df/retrieved_df.json.zip"
    backup_path = "./output/retrieved_df/retrieved_df.json.zip.bak"
    df = load_retrieved_df(zip_path)
    df = normalize_df(df)
    storage = Storage(root="./storage", duckdb_path="./storage/cadmus.duckdb")
    storage.init_tables()
    # upsert into articles table and register under a migration project
    migrated = storage.upsert_articles(df, project_id="migration_import")
    # backup original
    if os.path.exists(zip_path):
        shutil.copy(zip_path, backup_path)
    print(f"Migrated {len(migrated)} rows to parquet at {storage._table_path('articles')}")


if __name__ == "__main__":
    main()
