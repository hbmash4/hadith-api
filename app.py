import os
import sqlite3
import re
from fastapi import FastAPI, HTTPException

DB_PATH = os.getenv("DB_PATH", "SunnahDb.db")

app = FastAPI()

ARABIC_SPACES_REGEX = re.compile(r"\s+")
HARAKAT_REGEX = re.compile(r"[\u064B-\u0652\u0670\u06D6-\u06ED]")

def normalize_spaces(text: str) -> str:
    return ARABIC_SPACES_REGEX.sub(" ", text).strip()

def remove_harakat(text: str) -> str:
    return HARAKAT_REGEX.sub("", text)

def clean_arabic_text(text: str) -> str:
    return normalize_spaces(remove_harakat(text))

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/hadith/random")
def random_hadith():
    MAX_LEN = 400

    conn = get_conn()
    rows = conn.execute(
        """
        SELECT Id, Book, Number, HadithText
        FROM Hadiths
        WHERE lower(Book) IN ('bukhari', 'muslim')
          AND LENGTH(HadithText) <= 800
        ORDER BY RANDOM()
        LIMIT 20;
        """
    ).fetchall()
    conn.close()

    for row in rows:
        clean_text = clean_arabic_text(row["HadithText"])
        if len(clean_text) <= MAX_LEN:
            return {
                "id": row["Id"],
                "book": row["Book"],
                "number": row["Number"],
                "hadithText": clean_text,
                "length": len(clean_text),
            }

    raise HTTPException(status_code=404, detail="No hadith found")
