import os
import uuid
import hashlib
from datetime import datetime
import pandas as pd
import duckdb


class Storage:
    def __init__(self, root="./storage", duckdb_path=None):
        self.root = root
        self.parquet_root = os.path.join(self.root, "parquet")
        self.artifact_root = os.path.join(self.root, "artifacts")
        os.makedirs(self.parquet_root, exist_ok=True)
        os.makedirs(self.artifact_root, exist_ok=True)
        self.duckdb_path = duckdb_path
        if duckdb_path:
            self.con = duckdb.connect(duckdb_path)
        else:
            self.con = duckdb.connect(database=":memory:")

    def _table_path(self, table_name):
        return os.path.join(self.parquet_root, f"{table_name}.parquet")

    def init_tables(self):
        # create empty parquet files / duckdb tables if not present
        tables = [
            "articles",
            "full_text_links",
            "file_artifacts",
            "parsed_texts",
            "projects",
        ]
        for t in tables:
            p = self._table_path(t)
            if not os.path.exists(p):
                pd.DataFrame().to_parquet(p)

    def query_duckdb(self, sql, params=None):
        return self.con.execute(sql, params or {}).fetchdf()

    def find_articles_by_identifiers(self, dois=None, pmids=None, pmcids=None):
        conds = []
        if dois is not None:
            dois = [d for d in (dois if isinstance(dois, (list, tuple)) else [dois])]
            conds.append(f"doi IN ({','.join([repr(d) for d in dois])})")
        if pmids is not None:
            pmids = [p for p in (pmids if isinstance(pmids, (list, tuple)) else [pmids])]
            conds.append(f"pmid IN ({','.join([repr(p) for p in pmids])})")
        if pmcids is not None:
            pmcids = [p for p in (pmcids if isinstance(pmcids, (list, tuple)) else [pmcids])]
            conds.append(f"pmcid IN ({','.join([repr(p) for p in pmcids])})")
        if not conds:
            return pd.DataFrame()
        p = self._table_path("articles")
        if os.path.exists(p):
            df = pd.read_parquet(p)
            q = " or ".join(conds)
            return df.query(q)
        return pd.DataFrame()

    def upsert_articles(self, df: pd.DataFrame, project_id: str = None):
        p = self._table_path("articles")
        df = df.copy()
        now = pd.Timestamp(datetime.utcnow())
        if "article_id" not in df.columns:
            df["article_id"] = [str(uuid.uuid4()) for _ in range(len(df))]
        if "first_seen" not in df.columns:
            df["first_seen"] = now
        df["last_seen"] = now

        # If a disk-backed DuckDB connection is available, try SQL MERGE for upsert
        if getattr(self, "duckdb_path", None):
            try:
                # register incoming dataframe
                self.con.register("_incoming_articles", df)

                # ensure articles table exists by loading parquet if present
                if os.path.exists(p) and os.path.getsize(p) > 0:
                    # create or replace table from parquet
                    self.con.execute(f"CREATE OR REPLACE TABLE articles AS SELECT * FROM read_parquet('{p}')")
                else:
                    # create empty articles table with incoming schema
                    self.con.execute("CREATE OR REPLACE TABLE articles AS SELECT * FROM _incoming_articles WHERE 1=0")

                # compute union of columns
                cols = df.columns.tolist()
                set_clause = ", ".join([f"{c}=s.{c}" for c in cols])

                # build MERGE statement using doi/pmid/pmcid matching
                merge_sql = (
                    "MERGE INTO articles AS t USING _incoming_articles AS s "
                    "ON (t.doi = s.doi OR (t.pmid IS NOT NULL AND t.pmid = s.pmid) OR (t.pmcid IS NOT NULL AND t.pmcid = s.pmcid)) "
                    f"WHEN MATCHED THEN UPDATE SET {set_clause} "
                    f"WHEN NOT MATCHED THEN INSERT ({', '.join(cols)}) VALUES ({', '.join(['s.'+c for c in cols])})"
                )

                self.con.execute(merge_sql)

                # persist back to parquet
                self.con.execute(f"COPY (SELECT * FROM articles) TO '{p}' (FORMAT PARQUET)")

                result = self.con.execute("SELECT * FROM articles").fetchdf()

                # register project links if requested
                if project_id is not None and not result.empty:
                    proj_p = self._table_path("projects")
                    if os.path.exists(proj_p) and os.path.getsize(proj_p) > 0:
                        proj_df = pd.read_parquet(proj_p)
                        # ensure required columns present
                        if not set(["project_id", "article_id", "added_at", "notes"]).issubset(set(proj_df.columns)):
                            proj_df = pd.DataFrame(columns=["project_id", "article_id", "added_at", "notes"])
                    else:
                        proj_df = pd.DataFrame(columns=["project_id", "article_id", "added_at", "notes"])
                    now_s = datetime.utcnow()
                    for aid in result["article_id"]:
                        if not ((proj_df["project_id"] == project_id) & (proj_df["article_id"] == aid)).any():
                            proj_df = pd.concat([proj_df, pd.DataFrame([{"project_id": project_id, "article_id": aid, "added_at": now_s, "notes": ""}])], ignore_index=True)
                    proj_df.to_parquet(proj_p, index=False)

                return result
            except Exception:
                # on any failure fall back to pandas implementation below
                pass

        # Fallback: pandas-based upsert
        if os.path.exists(p) and os.path.getsize(p) > 0:
            existing = pd.read_parquet(p)
        else:
            existing = pd.DataFrame()

        # simple dedupe by DOI/PMID/PMC: replace rows with same doi or pmid
        if not existing.empty:
            for idx, row in df.iterrows():
                mask = False
                if pd.notna(row.get("doi")):
                    mask = existing["doi"] == row.get("doi")
                if (not mask.any()) and pd.notna(row.get("pmid")):
                    mask = existing["pmid"] == row.get("pmid")
                if (not mask.any()) and pd.notna(row.get("pmcid")):
                    mask = existing["pmcid"] == row.get("pmcid")
                if mask.any():
                    ix = existing[mask].index[0]
                    for c in df.columns:
                        existing.at[ix, c] = row[c]
                    existing.at[ix, "last_seen"] = now
                else:
                    existing = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
            result = existing
        else:
            result = df
        result.to_parquet(p, index=False)
        # register project links
        if project_id is not None and not result.empty:
            proj_p = self._table_path("projects")
            if os.path.exists(proj_p) and os.path.getsize(proj_p) > 0:
                proj_df = pd.read_parquet(proj_p)
                if not set(["project_id", "article_id", "added_at", "notes"]).issubset(set(proj_df.columns)):
                    proj_df = pd.DataFrame(columns=["project_id", "article_id", "added_at", "notes"])
            else:
                proj_df = pd.DataFrame(columns=["project_id", "article_id", "added_at", "notes"])
            now_s = datetime.utcnow()
            for aid in result["article_id"]:
                if not ((proj_df["project_id"] == project_id) & (proj_df["article_id"] == aid)).any():
                    proj_df = pd.concat([proj_df, pd.DataFrame([{"project_id": project_id, "article_id": aid, "added_at": now_s, "notes": ""}])], ignore_index=True)
            proj_df.to_parquet(proj_p, index=False)
        return result

    def write_artifact(self, article_id, content: bytes, artifact_type: str, checksum: str = None):
        if checksum is None:
            checksum = hashlib.sha256(content).hexdigest()
        ext = artifact_type if artifact_type else "dat"
        sub = os.path.join(self.artifact_root, ext)
        os.makedirs(sub, exist_ok=True)
        fname = f"{checksum}.{ext}"
        path = os.path.join(sub, fname)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(content)
        # register artifact
        art_p = self._table_path("file_artifacts")
        if os.path.exists(art_p) and os.path.getsize(art_p) > 0:
            art_df = pd.read_parquet(art_p)
        else:
            art_df = pd.DataFrame(columns=["artifact_id", "article_id", "artifact_type", "storage_path", "file_size", "checksum", "parsed", "created_at"])
        aid = str(uuid.uuid4())
        stat = os.path.getsize(path)
        rec = {"artifact_id": aid, "article_id": article_id, "artifact_type": artifact_type, "storage_path": path, "file_size": stat, "checksum": checksum, "parsed": False, "created_at": datetime.utcnow()}
        art_df = pd.concat([art_df, pd.DataFrame([rec])], ignore_index=True)
        art_df.to_parquet(art_p, index=False)
        return aid, path

    def write_parsed_text(self, parsed_df: pd.DataFrame):
        p = self._table_path("parsed_texts")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            existing = pd.read_parquet(p)
            out = pd.concat([existing, parsed_df], ignore_index=True)
        else:
            out = parsed_df
        out.to_parquet(p, index=False)
        return out

    def upsert_article_row(self, row: dict, project_id: str = None):
        """Upsert a single article represented as a dict. Uses existing upsert_articles implementation."""
        df = pd.DataFrame([row])
        return self.upsert_articles(df, project_id=project_id)
