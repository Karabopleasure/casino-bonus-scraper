
#!/usr/bin/env python3
"""
Scrape welcome-bonus data for three casinos from BetProof.

Run from the project root:
    python scraper/scraper.py

Output:
    docs/bonuses.json

"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


SOURCE_URL = (
    "https://betproof.co.za/casino-bonuses-south-africa/"
    "sign-up-bonus-south-africa/"
)

CASINOS = ["Hollywoodbets", "Supabets", "PlayaBets"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "docs" / "bonuses.json"

USER_AGENT = "casino-bonus-screening-scraper/1.0"
REQUEST_DELAY_SECONDS = 2


def clean(text):
    """Normalize whitespace in extracted text."""
    return re.sub(r"\s+", " ", text or "").strip()


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
    })
    return session


def allowed_by_robots(url, session):
    """Check robots.txt before fetching the target page."""
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"

    try:
        response = session.get(robots_url, timeout=20)
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not check robots.txt: {exc}. Stopping safely."
        ) from exc

    # A server error or network problem should not be treated as permission.
    if response.status_code >= 500:
        raise RuntimeError(
            f"robots.txt returned HTTP {response.status_code}. Stopping."
        )

    # If robots.txt is missing (4xx), follow the usual crawler convention.
    if response.status_code >= 400:
        return True

    parser = robotparser.RobotFileParser()
    parser.parse(response.text.splitlines())

    return parser.can_fetch(USER_AGENT, url)


def fetch_page(url, session):
    """Fetch a public page without bypassing access controls."""
    try:
        response = session.get(url, timeout=30)
    except requests.RequestException as exc:
        raise RuntimeError(f"Page request failed: {exc}") from exc

    if response.status_code in (401, 403, 429):
        raise RuntimeError(
            f"Source returned HTTP {response.status_code}. "
            "Do not bypass the restriction; choose another permitted source."
        )

    if "captcha" in response.text[:10000].lower():
        raise RuntimeError(
            "A CAPTCHA page may have been returned. "
            "Do not bypass it; choose another permitted source."
        )

    response.raise_for_status()
    return response.text


def find_column(headers, keywords):
    """Find a table column using alternative header names."""
    for index, header in enumerate(headers):
        if any(word in header for word in keywords):
            return index
    return None


def parse_comparison_table(html):
    """Extract casino rows and their original bonus terms."""
    soup = BeautifulSoup(html, "html.parser")

    for table in soup.find_all("table"):
        header_row = table.find("tr")
        if not header_row:
            continue

        header_cells = header_row.find_all(["th", "td"])
        headers = [clean(cell.get_text(" ", strip=True)).lower()
                   for cell in header_cells]

        casino_col = find_column(headers, ["casino"])
        bonus_col = find_column(headers, ["bonus"])
        wagering_col = find_column(
            headers, ["wagering", "rollover", "playthrough"]
        )
        deposit_col = find_column(
            headers, ["min deposit", "minimum deposit", "deposit"]
        )

        if casino_col is None or bonus_col is None:
            continue

        results = {}

        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])

            if len(cells) <= max(casino_col, bonus_col):
                continue

            # Skip the table header itself.
            if tr.find("th"):
                continue

            casino_name = clean(
                cells[casino_col].get_text(" ", strip=True)
            )

            if not casino_name:
                continue

            def cell_text(index):
                if index is None or index >= len(cells):
                    return None
                value = clean(cells[index].get_text(" ", strip=True))
                return value or None

            normalized_name = re.sub(
                r"\s+claim\s*.*$", 
                "", 
                casino_name, 
                flags=re.IGNORECASE
            ).strip()

            results[normalized_name.casefold()] = {
                "casino": normalized_name,
                "welcome_bonus": cell_text(bonus_col),
                "wagering_requirement": cell_text(wagering_col),
                "min_deposit": cell_text(deposit_col),
            }

        if results:
            return results

    raise RuntimeError(
        "Could not find a comparison table with casino and bonus columns. "
        "The source layout may have changed."
    )


def main():
    print("Checking robots.txt ...")

    session = create_session()

    if not allowed_by_robots(SOURCE_URL, session):
        sys.exit(
            "robots.txt does not permit this URL. "
            "Stop and choose another permitted source."
        )

    import time
    time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Fetching {SOURCE_URL}")

    try:
        html = fetch_page(SOURCE_URL, session)
        rows = parse_comparison_table(html)
    except (RuntimeError, requests.RequestException) as exc:
        sys.exit(f"Scraping stopped: {exc}")

    casinos = []

    for requested_name in CASINOS:
        row = rows.get(requested_name.casefold())

        if row is None:
            available = sorted(item["casino"] for item in rows.values())
            print(
                f"WARNING: {requested_name} was not found. "
                f"Available names: {available}",
                file=sys.stderr,
            )
            continue

        # Preserve the original source terms. Do not invent missing values.
        casinos.append({
            **row,
            "source_url": SOURCE_URL,
        })

        print(
            f"Found: {row['casino']} | "
            f"Bonus: {row['welcome_bonus']} | "
            f"Wagering: {row['wagering_requirement']} | "
            f"Deposit: {row['min_deposit']}"
        )

    if not casinos:
        sys.exit("No requested casinos were found. No output written.")

    payload = {
        "source": SOURCE_URL,
        "scraped_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "casinos": casinos,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(casinos)} casinos to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
