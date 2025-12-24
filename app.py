
import os
import sqlite3
from fastapi import FastAPI, Header, HTTPException

DB_PATH = os.getenv("DB_PATH", "SunnahDb.db")
API_KEY = os.getenv("API_KEY")  # set in Render dashboard

app = FastAPI(docs_url=None, redoc_url=None)  # optional: hide docs in public


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def require_key(x_api_key: str | None):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/hadith/random")
def random_hadith(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    require_key(x_api_key)

    conn = get_conn()
    row = conn.execute(
        """
        SELECT Id, Book, Number, HadithText
        FROM Hadiths
        WHERE lower(Book) IN ('bukhari', 'muslim')
        ORDER BY RANDOM()
        LIMIT 1;
        """
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No hadith found")

    return {
        "id": row["Id"],
        "book": row["Book"],
        "number": row["Number"],
        "hadithText": row["HadithText"],
    }

# import sqlite3
# from fastapi import FastAPI, HTTPException

# DB_PATH = "SunnahDb.db"

# app = FastAPI(title="Sunnah Hadith API", version="1.0.0")


# def get_conn():
#     conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn


# @app.get("/hadith/random")
# def random_hadith():
#     try:
#         conn = get_conn()
#         cur = conn.cursor()

#         row = cur.execute("""
#             SELECT Id, Book, Number, HadithText
#             FROM Hadiths
#             WHERE Book IN ('bukhari', 'muslim')
#             ORDER BY RANDOM()
#             LIMIT 1;
#         """).fetchone()

#         conn.close()

#         if not row:
#             raise HTTPException(status_code=404, detail="No hadith found")

#         return {
#             "id": row["Id"],
#             "book": row["Book"],
#             "number": row["Number"],
#             "hadith": row["HadithText"]
#         }

#     except sqlite3.Error as e:
#         raise HTTPException(status_code=500, detail=str(e))
