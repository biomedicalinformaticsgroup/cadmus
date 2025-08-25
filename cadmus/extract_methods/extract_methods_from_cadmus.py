import argparse
from pathlib import Path
from typing import Optional
import pandas as pd

from cadmus.extract_methods.utils import (
    read_retrieved_dataframe,
    ensure_dir,
    setup_logger,
    write_summary_stats,
)

from cadmus.extract_methods.xml_extractor import (
    can_handle as xml_can_handle,
    extract_methods as xml_extract,
)
from cadmus.extract_methods.html_extractor import (
    can_handle as html_can_handle,
    extract_methods as html_extract,
)
from cadmus.extract_methods.pdf_extractor import (
    can_handle as pdf_can_handle,
    extract_methods as pdf_extract,
)
from cadmus.extract_methods.plain_extractor import (
    can_handle as plain_can_handle,
    extract_methods as plain_extract,
)


FORMAT_HANDLERS = [
    ("xml", xml_can_handle, xml_extract),
    ("html", html_can_handle, html_extract),
    ("pdf", pdf_can_handle, pdf_extract),
    ("plain", plain_can_handle, plain_extract),
]


def extract_methods(
    cadmus_base_dir: Path,
    output_base: Path,
    logs_base: Path,
    select_format: Optional[str] = None,
    logger=None,
):
    """
    Orchestrate extraction of 'Materials & Methods' sections from articles in various formats.

    This function performs the end-to-end Cadmus pipeline:
      1. Loads metadata from a JSON-compressed DataFrame.
      2. Filters to records that have at least one available format (XML, HTML, PDF, or Plain text).
      3. Optionally restricts to a single format via `select_format`, keeping only rows
         where that format flag is 1 and all other format flags are 0.
      4. Iterates over each remaining PMID and dispatches it to the first format handler
         (XML → HTML → PDF → Plain) whose `can_handle` method returns True.
      5. Collects success/failure counts and subtitle counts for each format and overall.
      6. Writes per-format and overall summary statistics to log files.

    Parameters:
        cadmus_base_dir (Path): Root directory containing retrieved data subfolder.
        wrong_csvs (list[Path]): List of CSV paths; any PMID in these files will be excluded.
        output_base (Path): Directory where extracted sections will be saved (one subdir per format).
        logs_base (Path): Directory where logs and summary statistics will be written.
        select_format (str | None): If provided, must be one of 'xml', 'html', 'pdf', or 'plain'.
            When set, only rows whose flag for this format is 1 and whose flags for all other
            formats are 0 will be processed. Use None (default) to process all available formats.
        logger (Logger | None): Optional Python logger instance. If None, a default logger is created.

    Returns:
        None: Summary files and extracted sections are written to disk; results are not returned.
    """
    cadmus_base_dir = Path(cadmus_base_dir)
    output_base = Path(output_base)
    logs_base = Path(logs_base)
    
    if logger is None:
        logger = setup_logger("cadmus_pipeline", log_file=logs_base / "pipeline.log")

    # --- load & initial filter steps omitted for brevity ---
    df_all = read_retrieved_dataframe(cadmus_base_dir / "retrieved_df" / "retrieved_df2.json.zip")
    df_filtered = df_all.copy()
    print(f"Loaded {df_filtered.shape[0]} records from file {cadmus_base_dir}")
    
    # keep only rows with at least one format-flag
    formats = ["xml", "html", "pdf", "plain"]
    mask_any = df_filtered[formats].any(axis=1)
    df_filtered = df_filtered[mask_any]
    print(f"Filtered to {df_filtered.shape[0]} records with at least one format")

    # --- parameterized select_format logic ---
    if select_format is not None:
        if select_format not in formats:
            raise ValueError(f"select_format must be one of {formats!r}, not {select_format!r}")
        others = [f for f in formats if f != select_format]
        mask_only = (
            (df_filtered[select_format] == 1) &
            (df_filtered[others].sum(axis=1) == 0)
        )
        logger.info(f"Applying select_format={select_format!r}: "
                    f"{mask_only.sum()} rows with only that format")
        df_filtered = df_filtered[mask_only]


    # 4) Prepare counters
    overall_total = 0
    overall_success = 0
    overall_subtitles = []

    format_stats = {
        fmt: {"total": 0, "success": 0, "subtitles": []}
        for fmt, _, _ in FORMAT_HANDLERS
    }

    # 5) Ensure base output/log directories exist
    ensure_dir(output_base)
    ensure_dir(logs_base)

    # 6) Iterate through each PMID row
    for idx, row in df_filtered.iterrows():
        pmid = row["pmid"]
        overall_total += 1

        # We’ll keep going through all formats until one actually succeeds.
        handled = False
        for fmt_name, can_handle, extract in FORMAT_HANDLERS:
            can_handle, correct_file_path = can_handle(pmid, cadmus_base_dir, row, logger)
            
            if not can_handle:
                continue

            format_stats[fmt_name]["total"] += 1

            out_dir = output_base / fmt_name
            log_dir = logs_base / fmt_name
            ensure_dir(out_dir)
            ensure_dir(log_dir)

            logger.info(f"[{fmt_name.upper()}] Attempting PMID {pmid}")
            try:
                success, count = extract(
                    pmid=pmid,
                    file_path=correct_file_path,
                    output_dir=out_dir,
                    logs_dir=log_dir,
                    logger=logger,
                )
            except Exception as e:
                logger.error(f"[{fmt_name.upper()}][ERROR] Extraction exception for {pmid}: {e}")
                success, count = False, 0

            if success:
                # Once a format succeeds, we stop trying lower‐priority formats.
                format_stats[fmt_name]["success"] += 1
                format_stats[fmt_name]["subtitles"].append(count)
                overall_success += 1
                overall_subtitles.append(count)
                handled = True
                break
            else:
                # This format could “handle” but failed → try the next one
                logger.warning(f"[{fmt_name.upper()}] Failed for PMID {pmid}, trying next format…")
                # don’t set handled=True, so the loop continues

        if not handled:
            # No format both “could handle” and “succeeded”
            missing_log = logs_base / "missing_files.txt"
            ensure_dir(missing_log.parent)
            with open(missing_log, "a") as f:
                f.write(f"{pmid}\n")
            logger.warning(f"No format succeeded for PMID {pmid}")
        else:
            logger.info(f"Successfully processed PMID {pmid} with {fmt_name.upper()} format")

    # 7) Write per-format summary stats
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M")
    for fmt_name, stats in format_stats.items():
        summary_path = logs_base / fmt_name / f"summary_stats_{fmt_name}_{timestamp}.txt"
        write_summary_stats(
            out_path=summary_path,
            total=stats["total"],
            success=stats["success"],
            subtitle_counts=stats["subtitles"],
        )
        logger.info(f"Wrote {fmt_name.upper()} summary to {summary_path}")

    # 8) Write overall summary
    overall_summary = logs_base / f"overall_summary_stats_{timestamp}.txt"
    write_summary_stats(
        out_path=overall_summary,
        total=overall_total,
        success=overall_success,
        subtitle_counts=overall_subtitles,
    )
    logger.info(f"Wrote overall summary to {overall_summary}")
    logger.info("All processing complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Orchestrate CADMUS full-text → extract Materials & Methods (XML, HTML, PDF, Plain)"
    )
    parser.add_argument(
        "--cadmus-dir",
        type=Path,
        default=Path("./output"),
        help="Base directory where CADMUS placed its output (contains retrieved_df2.json.zip)",
    )
    parser.add_argument(
        "--output-base",
        type=Path,
        default=Path("./materials_methods"),
        help="Root directory under which format-specific JSONs will be written",
    )
    parser.add_argument(
        "--logs-base",
        type=Path,
        default=Path("./materials_methods/logs"),
        help="Root directory under which logs and summary files will be placed",
    )
    
    parser.add_argument(
        "--select-format",
        type=str,
        choices=["plain", "xml", "html", "pdf"],
        default=None,
        help=(
            "If set, only keep rows whose flag for this format is 1 "
            "and whose flags for all other formats are 0. "
            "One of plain, xml, html or pdf."
        ),
    )
    args = parser.parse_args()

    extract_methods(
        cadmus_base_dir=args.cadmus_dir,
        output_base=args.output_base,
        logs_base=args.logs_base,
        select_format=args.select_format if args.select_format else None,
    )
