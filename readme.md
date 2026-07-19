# SEO Keywords Plugin

Tooling to insert and fetch SEO seed keywords per market, stored in a MariaDB/MySQL database.

## Requirements

- Python 3.10+ (tested with Python 3.14)
- Access to a running MariaDB/MySQL server
- pip

## 1. Clone / navigate to the project

```bash
cd ~/Downloads/seo-keywords-plugin
```

## 2. Create and activate a virtual environment

Using a venv keeps dependencies isolated from your system Python.

```bash
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now show `(venv)` at the start of the line. Every time you work on this project, activate the venv first:

```bash
source venv/bin/activate
```

To leave the venv when you're done:

```bash
deactivate
```

## 3. Install the required modules

This project needs two packages that aren't part of the standard library:

- **pymysql** — MySQL/MariaDB database driver
- **python-dotenv** — loads environment variables from a `.env` file

Install them with:

```bash
pip install pymysql python-dotenv
```

If pip complains with an "externally-managed-environment" error (only relevant if you're *not* using a venv), use:

```bash
pip install pymysql python-dotenv --break-system-packages
```

To confirm both are installed correctly:

```bash
pip show pymysql
pip show python-dotenv
```

## 4. Configure environment variables

The script loads configuration from a `.env` file. It looks in this order:

1. `/opt/data/.env` (used when running inside the Hermes container)
2. `.env` in the project root (used for local development) — i.e. `~/Downloads/seo-keywords-plugin/.env`

Create a local `.env` file if it doesn't already exist:

```bash
touch .env
```

Add the following variables, adjusted to match your database:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_AMZ=seo
DB_USER=root
DB_PASSWORD=your_password_here
```

| Variable      | Description                          | Default       |
|---------------|---------------------------------------|---------------|
| `DB_HOST`     | Database host                         | `127.0.0.1`   |
| `DB_PORT`     | Database port                         | `3306`        |
| `DB_AMZ`      | Database/schema name                  | `seo`         |
| `DB_USER`     | Database user                         | `root`        |
| `DB_PASSWORD` | Database password                     | *(empty)*     |

> **Note:** if these values are missing or incorrect, the script falls back to the defaults above, which may cause a `Connection refused` error if no database is listening there.

## 5. Make sure the database server is running

Check that MariaDB/MySQL is running and listening on the expected port:

```bash
sudo systemctl status mariadb
# or
sudo systemctl status mysql
```

Confirm it's listening on the expected port:

```bash
sudo ss -ltnp | grep 3306
```

## 6. Run the project

With the venv activated and `.env` configured:

```bash
python tools.py
```

By default, `main()` runs `test_get_existing_seed_keywords()`, which fetches existing seed keywords for the `fr` market and prints the result as JSON.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'pymysql'` | Package not installed in the active environment | `pip install pymysql` (make sure venv is activated) |
| `Can't connect to MySQL server ... Connection refused` | No DB server running on that host/port, or `.env` not loaded | Check `.env` location/values, confirm DB service is running |
| `.env` values not picked up | `python-dotenv` not installed, or `.env` file missing/misplaced | `pip install python-dotenv`; verify file exists at `/opt/data/.env` or project root |