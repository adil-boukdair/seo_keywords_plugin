"""Tool handlers — the code that runs when the LLM calls each tool."""

import json
import logging
import os
from pathlib import Path
 
logger = logging.getLogger(__name__)
 
# Load /opt/data/.env (Hermes main env file)
# Falls back to a local .env when running outside the container (local dev)
try:
    from dotenv import load_dotenv
    _env_file = Path("/opt/data/.env")
    if not _env_file.exists():
        _env_file = Path(__file__).parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file, override=True)
        logger.info("seo-keywords: loaded env from %s", _env_file)
except ImportError:
    pass  # python-dotenv not installed — env vars must already be set by Hermes

# ---------------------------------------------------------------------------
# DB connection helper
# ---------------------------------------------------------------------------

def _get_connection():
    """Return a MariaDB/MySQL connection using SEO_DB_* env vars.

    Raises on failure — callers must wrap in try/except and return error JSON.
    Requires: pip install pymysql
    """
    import pymysql  # imported lazily so missing lib gives a clean check_fn=False

    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_AMZ", "seo"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        connect_timeout=5,
        autocommit=False,
        charset="utf8mb4",
    )


def _ensure_table(cursor):
    """Create the seed_keywords table if it doesn't exist yet."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seed_keywords (
            id            INT          NOT NULL AUTO_INCREMENT,
            market        VARCHAR(255) NOT NULL,
            seed_keyword  VARCHAR(512) NOT NULL,
            created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY uq_market_keyword (market, seed_keyword)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)


# ---------------------------------------------------------------------------
# Tool 1: insert_seed_keywords
# ---------------------------------------------------------------------------

def insert_seed_keywords(market: str, seed_keywords: list) -> str:
    """Insert seed keywords for a market into MariaDB.

    Uses INSERT IGNORE so duplicate (market, seed_keyword) pairs are
    silently skipped without raising an error.
    """

    # --- Input validation ---
    if not market:
        return json.dumps({"error": "Parameter 'market' is required and cannot be empty."})

    if not seed_keywords or not isinstance(seed_keywords, list):
        return json.dumps({"error": "Parameter 'seed_keywords' must be a non-empty list of strings."})

    # Normalise: strip whitespace, drop empty entries, deduplicate within request
    cleaned = list(dict.fromkeys(kw.strip() for kw in seed_keywords if str(kw).strip()))
    if not cleaned:
        return json.dumps({"error": "All provided seed_keywords were empty after stripping whitespace."})

    # --- DB write ---
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        #_ensure_table(cursor)

        inserted = 0
        skipped = 0

        for kw in cleaned:
            cursor.execute(
                "INSERT IGNORE INTO seed_keywords (market, keyword) VALUES (%s, %s)",
                (market, kw),
            )
            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(
            "insert_seed_keywords: market=%r inserted=%d skipped=%d",
            market, inserted, skipped,
        )

        return json.dumps({
            "success": True,
            "market": market,
            "inserted": inserted,
            "skipped_duplicates": skipped,
            "keywords_processed": cleaned,
        })

    except Exception as exc:
        logger.exception("insert_seed_keywords failed")
        return json.dumps({"error": f"Database error: {exc}"})


# ---------------------------------------------------------------------------
# Tool 2: analyze_keyword_opportunities (placeholder)
# ---------------------------------------------------------------------------

def analyze_keyword_opportunities(args: dict, **kwargs) -> str:
    """Placeholder — not yet implemented."""
    market: str = args.get("market", "").strip()
    mode: str = args.get("mode", "expand")

    return json.dumps({
        "error": "not_implemented",
        "message": (
            f"analyze_keyword_opportunities (mode={mode!r}, market={market!r}) "
            "is a placeholder and has not been implemented yet. "
            "This tool is reserved for future development."
        ),
    })

# ---------------------------------------------------------------------------
# Tool 3: get_existing_seed_keywords
# ---------------------------------------------------------------------------
def get_existing_seed_keywords_by_market(market: str) -> str:
    """Return the existing seed keywords for a market separated by comma."""

    if not market or not market.strip():
        return json.dumps({"error": "Parameter 'market' is required and cannot be empty."})

    try:
        conn = _get_connection()
        cursor = conn.cursor()
        _ensure_table(cursor)

        cursor.execute(
            "SELECT keyword FROM seed_keywords WHERE market = %s ORDER BY keyword ASC",
            (market.strip(),),
        )
        keywords = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        logger.info(
            "get_existing_seed_keywords_by_market: market=%r keywords_found=%d",
            market.strip(), len(keywords),
        )

        return ", ".join(keywords)
        return json.dumps({
            "success": True,
            "market": market.strip(),
            "existing_seed_keywords": keywords,
        })

    except Exception as exc:
        logger.exception("get_existing_seed_keywords_by_market failed")
        return json.dumps({"error": f"Database error: {exc}"})

# ---------------------------------------------------------------------------
# Availability check (shared by both tools)
# ---------------------------------------------------------------------------

def check_db_requirements() -> bool:
    """Return True only if pymysql is importable and all required env vars are set."""
    try:
        import pymysql  # noqa: F401
    except ImportError:
        logger.warning("seo-keywords plugin: 'pymysql' package not installed. Run: pip install pymysql")
        return False

    required = ["DB_HOST", "DB_AMZ", "DB_USER", "DB_PASSWORD"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        logger.warning("seo-keywords plugin: missing env vars: %s", missing)
        return False

    return True


def main() -> None:


    result = test_get_existing_seed_keywords()
    print(result)

def test_insert_seed_keywords(): 
    result = insert_seed_keywords(
        market= 'fr',
        seed_keywords= ['Ihram', 'parapluie'],
    )
    print(result)

def test_get_existing_seed_keywords():
    result = get_existing_seed_keywords_by_market(
        market= 'fr'
    )
    print(result)        
 


if __name__ == "__main__":
    main()
