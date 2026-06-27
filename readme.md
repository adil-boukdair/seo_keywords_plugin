# seo-keywords — Hermes Plugin

A Hermes Agent plugin to store SEO seed keywords into a MariaDB database, organized by market.

## What it does

| Tool | Status | Description |
|------|--------|-------------|
| `insert_seed_keywords` | ✅ Ready | Inserts seed keywords for a given market into MariaDB |
| `analyze_keyword_opportunities` | 🚧 Placeholder | Reserved for future keyword clustering / expansion |

---

## Plugin file structure

```
seo-keywords-plugin/
├── __init__.py       # Hermes entry point — wires schemas → handlers
├── plugin.yaml       # Plugin manifest — name, tools, required env vars
├── schemas.py        # LLM-facing tool descriptions and parameter specs
├── tools.py          # Actual logic — DB writes, placeholder handler
├── test_tools.py     # Local test script (do not deploy to Hermes)
└── README.md
```

---

## Database schema

The plugin auto-creates this table on first use if it doesn't exist:

```sql
CREATE TABLE IF NOT EXISTS seed_keywords (
    id            INT          NOT NULL AUTO_INCREMENT,
    market        VARCHAR(255) NOT NULL,
    seed_keyword  VARCHAR(512) NOT NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_market_keyword (market, seed_keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

Duplicate `(market, seed_keyword)` pairs are silently ignored via `INSERT IGNORE`.

---

## Local development & testing

### 1. Prerequisites

- Python 3.10+
- A running MariaDB or MySQL instance reachable from your machine

```bash
python3 --version
```

### 2. Create a virtual environment

```bash
cd seo-keywords-plugin

python3 -m venv .venv

# Activate — Linux/Mac
source .venv/bin/activate

# Activate — Windows
.venv\Scripts\activate
```

Your prompt will show `(.venv)` when the venv is active.

### 3. Install dependencies

```bash
pip install pymysql
```

### 4. Create the test script

Create `test_tools.py` in the plugin folder:

```python
"""Quick local test for insert_seed_keywords."""

import os
import sys

# --- Set your DB credentials here for local testing ---
os.environ["SEO_DB_HOST"] = "127.0.0.1"
os.environ["SEO_DB_PORT"] = "3306"
os.environ["SEO_DB_NAME"] = "seo"
os.environ["SEO_DB_USER"] = "root"
os.environ["SEO_DB_PASSWORD"] = "yourpassword"

sys.path.insert(0, os.path.dirname(__file__))

from tools import insert_seed_keywords, analyze_keyword_opportunities, check_db_requirements

# Test 1: check requirements
print("=== check_db_requirements ===")
ok = check_db_requirements()
print(f"  result: {ok}")
assert ok, "Requirements check failed — check your env vars and pymysql install"

# Test 2: insert keywords
print("\n=== insert_seed_keywords (first insert) ===")
result = insert_seed_keywords({
    "market": "running shoes",
    "seed_keywords": [
        "best running shoes",
        "trail running shoes",
        "minimalist running shoes",
        "running shoes for flat feet",
    ]
})
print(f"  result: {result}")

# Test 3: insert again — should all be duplicates
print("\n=== insert_seed_keywords (duplicates) ===")
result = insert_seed_keywords({
    "market": "running shoes",
    "seed_keywords": ["best running shoes", "trail running shoes"]
})
print(f"  result: {result}")

# Test 4: empty market validation
print("\n=== insert_seed_keywords (empty market) ===")
result = insert_seed_keywords({"market": "", "seed_keywords": ["test"]})
print(f"  result: {result}")

# Test 5: placeholder tool
print("\n=== analyze_keyword_opportunities (placeholder) ===")
result = analyze_keyword_opportunities({"market": "running shoes", "mode": "expand"})
print(f"  result: {result}")

print("\n✓ All tests passed")
```

### 5. Run the tests

```bash
python test_tools.py
```

Expected output:

```
=== check_db_requirements ===
  result: True

=== insert_seed_keywords (first insert) ===
  result: {"success": true, "market": "running shoes", "inserted": 4, "skipped_duplicates": 0, ...}

=== insert_seed_keywords (duplicates) ===
  result: {"success": true, "market": "running shoes", "inserted": 0, "skipped_duplicates": 2, ...}

=== insert_seed_keywords (empty market) ===
  result: {"error": "Parameter 'market' is required and cannot be empty."}

=== analyze_keyword_opportunities (placeholder) ===
  result: {"error": "not_implemented", "message": "..."}

✓ All tests passed
```

### 6. Verify in the database

```sql
SELECT * FROM seed_keywords ORDER BY created_at DESC;
```

---

## Deploying to Hermes (Docker)

### Step 1 — Copy the plugin into your .hermes volume

```bash
cp -r seo-keywords-plugin /home/ubuntu/docker/hermes/.hermes/plugins/seo-keywords
```

Do **not** copy `test_tools.py` or `.venv/` — those are local-only.

### Step 2 — Set DB credentials in .env

Add these to `/home/ubuntu/docker/hermes/.hermes/.env`:

```env
SEO_DB_HOST=your-mariadb-host
SEO_DB_PORT=3306
SEO_DB_NAME=seo
SEO_DB_USER=youruser
SEO_DB_PASSWORD=yourpassword
```

### Step 3 — Install pymysql into the container

`pymysql` must be installed inside the container. The recommended approach is to update your `docker-compose.yml` to install it automatically on every start:

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: >
      bash -c "/opt/hermes/.venv/bin/pip install pymysql --quiet &&
               gateway run"
    volumes:
      - ./.hermes:/opt/data
    environment:
      - HERMES_DASHBOARD_ARGS=--host 0.0.0.0 --port 9119 --no-open --skip-build
      - HERMES_DASHBOARD=1
      - HERMES_DASHBOARD_INSECURE=0
      - GATEWAY_ALLOW_ALL_USERS=true
    ...
```

> **Why not just `docker exec hermes pip install pymysql`?**
> A manual install is wiped every time the container is recreated (image update, `docker compose down && up`).
> The `command` trick re-runs pip on every start — pip is instant when the package is already cached.

**Alternative: Dockerfile (more robust)**

If you prefer baking it into a custom image:

```dockerfile
FROM nousresearch/hermes-agent:latest
RUN /opt/hermes/.venv/bin/pip install pymysql
```

Then in `docker-compose.yml`:
```yaml
services:
  hermes:
    build: .
    image: hermes-custom
    command: gateway run
    ...
```

Rebuild after any change:
```bash
docker compose build
docker compose up -d
```

### Step 4 — Restart and verify

```bash
docker compose up -d
```

Check the Hermes startup banner — you should see:

```
✓ seo-keywords v1.0.0 (2 tools)
```

Or run inside the gateway chat:

```
/plugins
```

---

## Using the tool

Once deployed, just talk to Hermes naturally:

> *"Add these seed keywords to the running shoes market: best running shoes, trail running shoes, minimalist running shoes"*

> *"Store the following keywords under the keto diet market: keto meal plan, keto for beginners, keto recipes"*

---

## Environment variables reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SEO_DB_HOST` | ✅ | `127.0.0.1` | MariaDB host |
| `SEO_DB_PORT` | ❌ | `3306` | MariaDB port |
| `SEO_DB_NAME` | ✅ | `seo` | Database name |
| `SEO_DB_USER` | ✅ | `root` | Database user |
| `SEO_DB_PASSWORD` | ✅ | *(empty)* | Database password |

---

## .gitignore

If you use git, add these:

```
.venv/
test_tools.py
```