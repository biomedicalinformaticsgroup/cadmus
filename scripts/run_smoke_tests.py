#!/usr/bin/env python3
# scripts/run_smoke_tests.py
import sys
from pathlib import Path

def test_storage():
    print("== Storage test ==")
    # Import Storage directly from the module file to avoid importing package
    # level `cadmus.__init__` which pulls in many optional deps during smoke tests.
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "cadmus.storage",
        Path(__file__).resolve().parent.parent / "cadmus" / "storage.py",
    )
    storage_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(storage_mod)
    Storage = storage_mod.Storage
    import pandas as pd
    s = Storage(root="./storage", duckdb_path="./storage/cadmus.duckdb")
    s.init_tables()
    # include project_id column so upsert_articles can associate rows with a project
    df = pd.DataFrame([
        {
            "doi": "10.1000/testdoi",
            "pmid": "12345",
            "title": "Test Title",
            "abstract": "Test abstract",
            "pmcid": None,
            "project_id": "test",
        }
    ])
    res = s.upsert_articles(df, project_id="test")
    print("Upserted rows:", len(res))
    print("Sample:", res.head().to_dict(orient="records"))
    try:
        # Storage exposes DuckDB connection as `con`
        tables = s.con.execute("SELECT table_name FROM information_schema.tables").fetchall()
        print("DuckDB tables:", tables)
    except Exception as e:
        print("DuckDB query error:", e)

def test_pdf(pdf_path):
    print("\n== PDF parsing test ==")
    # Import pdf_to_text directly to avoid importing package-level cadmus.__init__
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "cadmus.parsing.pdf_to_text",
        Path(__file__).resolve().parent.parent / "cadmus" / "parsing" / "pdf_to_text.py",
    )
    pdf_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pdf_mod)
    pdf_to_text = pdf_mod.pdf_to_text
    p = Path(pdf_path)
    if not p.exists():
        print("PDF not found:", p)
        print("Skipping PDF parsing test — provide a valid PDF path to exercise PDF parsing.")
        return
    try:
        text = pdf_to_text(str(p))
        print("Extracted text length:", len(text or ""))
        print("First 400 chars:\n", (text or "")[:400])
    except Exception as e:
        print("PDF parsing error:", type(e).__name__, e)

if __name__ == "__main__":
    test_storage()
    if len(sys.argv) > 1:
        test_pdf(sys.argv[1])
    else:
        print("\nNo PDF provided for pdf test. To run it: python scripts/run_smoke_tests.py /path/to/file.pdf")
