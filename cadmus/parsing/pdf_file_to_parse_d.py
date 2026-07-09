from cadmus.parsing.clean_pdf_body import clean_pdf_body
from cadmus.parsing.limit_body import limit_body
from cadmus.parsing.get_abstract_pdf import get_abstract_pdf
from cadmus.evaluation.abstract_similarity_score import abstract_similarity_score
from cadmus.evaluation.body_unique_score import body_unique_score
import os
from cadmus.parsing.pdf_to_text import pdf_to_text
import fitz
import os
import pandas as pd


def pdf_file_to_parse_d(retrieval_df, index, path_document, ftp_link, keep_abstract, storage=None, article_id=None):
    parse_d = {}
    # load pdf and extract text via PyMuPDF
    try:
        p_text = pdf_to_text(path_document)
        # basic validation
        if not isinstance(p_text, str) or p_text.strip() == "":
            p_text = ""
            Content_type = "error"
            parse_d.update({"Content_type": Content_type})
        else:
            # cleaning and limiting the text
            p_text = clean_pdf_body(p_text)
            p_text = limit_body(p_text, keep_abstract)
    except Exception:
        p_text = ""
        Content_type = "error"
        parse_d.update({"Content_type": Content_type})
        # return minimal parse_d
        return parse_d, p_text

        # check for abstract in storage (preferred) or retrieval_df
        ab = ""
        if storage is not None and article_id is not None:
            try:
                art_p = storage._table_path("articles")
                if os.path.exists(art_p) and os.path.getsize(art_p) > 0:
                    articles = pd.read_parquet(art_p)
                    row = articles[articles["article_id"] == article_id]
                    if not row.empty and "abstract" in row.columns:
                        val = row.iloc[0]["abstract"]
                        if val is not None and val != "":
                            ab = val
            except Exception:
                ab = ""

        if ab == "":
            if (
                retrieval_df.loc[index, "abstract"] != ""
                and retrieval_df.loc[index, "abstract"] != None
                and retrieval_df.loc[index, "abstract"] == retrieval_df.loc[index, "abstract"]
            ):
                ab = retrieval_df.loc[index, "abstract"]
            else:
                # try parse the abstract
                ab = get_abstract_pdf(p_text)

        # get the file_size
        size = os.stat(path_document).st_size
        # get the word_count
        wc = len(p_text.split())
        if ab != "" and ab != None:
            if type(ab) == str:
                wc_abs = len(ab.split())
            else:
                wc_abs = 0
        else:
            wc_abs = 0
        Content_type = "pdf"
        # extracting the date from PDF metadata if available
        try:
            doc = fitz.open(path_document)
            meta = doc.metadata or {}
            date = meta.get("creationDate") or meta.get("modDate") or meta.get("date")
            doc.close()
        except Exception:
            date = None
        # computhe the abs_similarity and the body_unique_score
        bu_score = body_unique_score(p_text, ab)
        as_score = abstract_similarity_score(p_text, ab)

        # use the output from each function to build a output dictionary to use for our evaluation and saving the information in case it's TP
        parse_d.update(
            {
                "file_path": f"./output/formats/pdfs/{index}.pdf.zip",
                "date": date,
                "size": size,
                "wc": wc,
                "wc_abs": wc_abs,
                "Content_type": Content_type,
                "url": ftp_link,
                "body_unique_score": bu_score,
                "ab_sim_score": as_score,
            }
        )

    return parse_d, p_text
