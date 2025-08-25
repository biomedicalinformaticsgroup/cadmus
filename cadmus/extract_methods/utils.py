# cadmus_extractors/utils.py

import os
import json
import zipfile
import logging
from pathlib import Path
from typing import Set

import pandas as pd

def setup_logger(name: str, log_file: Path = None, level=logging.INFO) -> logging.Logger:
    """
    Create (or retrieve) a logger that writes to stdout and optionally to a file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)   # <-- ensure folder exists
            fh = logging.FileHandler(str(log_file))
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    return logger


def ensure_dir(path: Path):
    """
    Make a directory (and all parents) if it does not exist.
    """
    path.mkdir(parents=True, exist_ok=True)


def read_retrieved_dataframe(json_zip_path: Path) -> pd.DataFrame:
    """
    Reads the zipped JSON file produced by CADMUS (“retrieved_df2.json.zip”)
    and returns a DataFrame with pmid as string.
    """
    with zipfile.ZipFile(str(json_zip_path), 'r') as z:
        name = z.namelist()[0]
        raw = z.read(name)
        data = json.loads(raw)
    df = pd.read_json(data, orient='index')
    df['pmid'] = df['pmid'].astype(str)
    return df


def write_summary_stats(
    out_path: Path,
    total: int,
    success: int,
    subtitle_counts: list[int]
):
    """
    Write a small summary‐stats text file. Ensures parent directory exists.
    """
    success_rate = (success / total) * 100 if total else 0
    avg_subs = (sum(subtitle_counts) / len(subtitle_counts)) if subtitle_counts else 0.0

    # Ensure parent directory exists before opening the file
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(str(out_path), 'w') as f:
        f.write("Summary Statistics:\n")
        f.write(f"  Total PMIDs processed           : {total}\n")
        f.write(f"  Successful methods extractions  : {success}\n")
        f.write(f"  Success rate                    : {success_rate:.2f}%\n")
        f.write(f"  Avg. unique subtitles extracted : {avg_subs:.2f}\n")
