#!/usr/bin/env python3
"""
=============================================================
Geneteka Genealogy Search Pipeline
https://geneteka.genealodzy.pl/
=============================================================

HOW THE CHALLENGE IS SOLVED
-----------------------------
Geneteka's public UI forces you to:
  1. Pick a region
  2. Then search only by SURNAME

But the underlying HTTP endpoint (op=gt) silently accepts a
`search_name` parameter for the given name too. This pipeline:

  Step 1.  Accepts a full name  e.g.  "Jan Kowalski"
  Step 2.  Splits it invisibly  → first="Jan", last="Kowalski"
  Step 3.  Fires GET requests with BOTH params against ALL 21
           regions × 3 record types (63 requests / person)
           in parallel using ThreadPoolExecutor
  Step 4.  Parses and aggregates HTML table results
  Step 5.  Returns a clean, structured summary

The caller only ever sees full names — the surname-only
constraint is bypassed entirely without the user knowing.

USAGE
-----
  python geneteka_search.py

  or import and call directly:

  from geneteka_search import run_pipeline
  results = run_pipeline("Jan Kowalski", "Maria Nowak")

DEPENDENCIES
------------
  pip install requests beautifulsoup4 lxml
"""

import sys
import time
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

BASE_URL = "https://geneteka.genealodzy.pl/index.php"

# Every province/region code on Geneteka (from the main page table)
REGIONS: Dict[str, str] = {
    "01ds": "Dolnośląskie",
    "02kp": "Kujawsko-Pomorskie",
    "03lb": "Lubelskie",
    "04ls": "Lubuskie",
    "05ld": "Łódzkie",
    "06mp": "Małopolskie",
    "07mz": "Mazowieckie",
    "71wa": "Warszawa",
    "08op": "Opolskie",
    "09pk": "Podkarpackie",
    "10pl": "Podlaskie",
    "11pm": "Pomorskie",
    "12sl": "Śląskie",
    "13sk": "Świętokrzyskie",
    "14wm": "Warmińsko-Mazurskie",
    "15wp": "Wielkopolskie",
    "16zp": "Zachodniopomorskie",
    "21uk": "Ukraina",
    "22br": "Białoruś",
    "23lt": "Litwa",
    "25po": "Pozostałe",
}

# Geneteka record type codes
RECORD_TYPES: Dict[str, str] = {
    "B": "Birth",
    "D": "Death",
    "S": "Marriage",
}

# HTTP request headers — polite browser-like UA
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://geneteka.genealodzy.pl/",
}

# Parallel workers — stay polite, don't hammer the server
MAX_WORKERS = 8

# Per-request timeout (seconds)
REQUEST_TIMEOUT = 20


# ─────────────────────────────────────────────────────────────
# DATA MODEL
# ─────────────────────────────────────────────────────────────

@dataclass
class GenetikaRecord:
    """One indexed genealogical record returned by Geneteka."""
    record_type: str             # Birth / Death / Marriage
    region: str                  # e.g. "Mazowieckie"
    year: Optional[str]          # Year of event
    surname: Optional[str]       # Family name
    first_name: Optional[str]    # Given name
    parish: Optional[str]        # Parish / registry office
    extra: Dict[str, str] = field(default_factory=dict)  # All raw columns

    def __str__(self) -> str:
        parts = [
            f"[{self.record_type}]",
            f"{self.first_name or '?'} {self.surname or '?'}",
            f"({self.year or '?'})",
            f"— {self.parish or 'unknown parish'}",
            f"| {self.region}",
        ]
        return "  " + "  ".join(parts)


# ─────────────────────────────────────────────────────────────
# NAME PARSING  (the "invisible" magic)
# ─────────────────────────────────────────────────────────────

def parse_full_name(full_name: str) -> Tuple[str, str]:
    """
    Split a full name into (first_name, last_name).

    Strategy:
    - Single word  → treat as surname, no given name
    - Two+ words   → everything but the last word = given name(s)
                     last word = surname

    Examples:
      "Jan Kowalski"         → ("Jan",        "Kowalski")
      "Maria Anna Nowak"     → ("Maria Anna", "Nowak")
      "Kowalski"             → ("",           "Kowalski")
    """
    parts = full_name.strip().split()
    if not parts:
        raise ValueError(f"Empty name provided: '{full_name}'")
    if len(parts) == 1:
        return ("", parts[0])
    return (" ".join(parts[:-1]), parts[-1])


# ─────────────────────────────────────────────────────────────
# HTML PARSING
# ─────────────────────────────────────────────────────────────

# Canonical English column names we care about (site returns both
# Polish and English depending on &lang=eng)
_YEAR_KEYS    = {"year", "rok"}
_SURNAME_KEYS = {"surname", "nazwisko", "last name"}
_NAME_KEYS    = {"name", "imię", "first name", "given name"}
_PARISH_KEYS  = {"parish", "parafia", "location", "place"}


def _find_col(headers: List[str], candidates: set) -> Optional[int]:
    """Return the first header index that matches any candidate keyword."""
    for i, h in enumerate(headers):
        if h.lower().strip() in candidates:
            return i
    # fallback: partial match
    for i, h in enumerate(headers):
        for c in candidates:
            if c in h.lower():
                return i
    return None


def parse_results_html(
    html: str, region_name: str, record_type_code: str
) -> List[GenetikaRecord]:
    """
    Parse the Geneteka results page HTML.

    Geneteka renders results as a <table> with a header row followed
    by data rows. We locate the right table by checking whether its
    header row contains recognisable column names.
    """
    soup = BeautifulSoup(html, "lxml")
    records: List[GenetikaRecord] = []
    record_type_label = RECORD_TYPES[record_type_code]

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        # ── Detect header row ──────────────────────────────────
        # The real results table has headers like Year / Surname / Name
        header_cells = rows[0].find_all(["th", "td"])
        headers = [c.get_text(strip=True).lower() for c in header_cells]

        # Must have at least one recognisable genealogy column
        all_keys = _YEAR_KEYS | _SURNAME_KEYS | _NAME_KEYS | _PARISH_KEYS
        if not any(h.strip() in all_keys or
                   any(k in h for k in all_keys) for h in headers):
            continue

        # Column index lookup
        yr_idx  = _find_col(headers, _YEAR_KEYS)
        sn_idx  = _find_col(headers, _SURNAME_KEYS)
        fn_idx  = _find_col(headers, _NAME_KEYS)
        par_idx = _find_col(headers, _PARISH_KEYS)

        # ── Data rows ──────────────────────────────────────────
        for row in rows[1:]:
            cells = row.find_all("td")
            if not cells:
                continue

            texts = [c.get_text(separator=" ", strip=True) for c in cells]
            if all(t == "" for t in texts):
                continue

            def get(idx):
                return texts[idx] if idx is not None and idx < len(texts) else None

            extra = {headers[i]: texts[i]
                     for i in range(min(len(headers), len(texts)))}

            records.append(GenetikaRecord(
                record_type=record_type_label,
                region=region_name,
                year=get(yr_idx),
                surname=get(sn_idx),
                first_name=get(fn_idx),
                parish=get(par_idx),
                extra=extra,
            ))

    return records


# ─────────────────────────────────────────────────────────────
# SINGLE SEARCH TASK  (one region × one record type)
# ─────────────────────────────────────────────────────────────

def _search_one(
    session: requests.Session,
    region_code: str,
    region_name: str,
    last_name: str,
    first_name: str,
    record_type: str,
) -> List[GenetikaRecord]:
    """
    Fire one GET request to Geneteka and return parsed records.

    KEY INSIGHT — the `search_name` parameter:
    The Geneteka website UI does NOT expose a first-name field on the
    main search page. However, the underlying op=gt endpoint silently
    accepts `search_name` for given-name filtering. We use this to
    pass the first name without the user needing to know it exists.

    URL structure discovered:
      ?op=gt          → "get territory" (search within a province)
      &lang=eng       → English column headers in the HTML
      &bdm=B/D/S      → record type: Births / Deaths / Marriages
      &w=07mz         → province code
      &rid=B/D/S      → same as bdm (required duplicate)
      &search_lastname=SURNAME
      &search_name=FIRSTNAME      ← hidden first-name filter
      &search_lastname2=          ← second person surname (marriage)
      &search_name2=              ← second person first name
      &from_date=&to_date=        ← year range (empty = all years)
      &exac=                      ← 1 for exact, empty for fuzzy
    """
    params = {
        "op": "gt",
        "lang": "eng",
        "bdm": record_type,
        "w": region_code,
        "rid": record_type,
        "search_lastname": last_name,
        "search_name": first_name,
        "search_lastname2": "",
        "search_name2": "",
        "from_date": "",
        "to_date": "",
        "exac": "",      # fuzzy matching (handles name variants)
    }

    try:
        resp = session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return parse_results_html(resp.text, region_name, record_type)
    except requests.exceptions.Timeout:
        print(f"    [timeout] {region_name} / {RECORD_TYPES[record_type]}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"    [error] {region_name} / {RECORD_TYPES[record_type]}: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# PER-PERSON SEARCH  (all regions × all record types)
# ─────────────────────────────────────────────────────────────

def search_person(full_name: str) -> List[GenetikaRecord]:
    """
    Search Geneteka for a single person by full name.

    Pipeline internals (invisible to the caller):
      1. Split full name → first name + surname
      2. Build 21 regions × 3 record types = 63 search tasks
      3. Execute in parallel with ThreadPoolExecutor
      4. Aggregate and return all matching records

    Args:
        full_name: e.g. "Jan Kowalski" or "Maria Anna Nowak"

    Returns:
        List of GenetikaRecord objects (may be empty).
    """
    first_name, last_name = parse_full_name(full_name)

    # Silently inform the developer (not the end user) what's happening
    print(f"  [pipeline] surname='{last_name}' | given name='{first_name}'")
    print(f"  [pipeline] Querying {len(REGIONS)} regions × "
          f"{len(RECORD_TYPES)} record types "
          f"({len(REGIONS) * len(RECORD_TYPES)} requests)...")

    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    all_records: List[GenetikaRecord] = []
    futures = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for region_code, region_name in REGIONS.items():
            for rt_code in RECORD_TYPES:
                f = executor.submit(
                    _search_one,
                    session, region_code, region_name,
                    last_name, first_name, rt_code,
                )
                futures[f] = (region_name, rt_code)

        completed = 0
        for future in as_completed(futures):
            records = future.result()
            all_records.extend(records)
            completed += 1
            # Simple progress tick
            if completed % 10 == 0 or completed == len(futures):
                print(f"  [pipeline] {completed}/{len(futures)} requests done, "
                      f"{len(all_records)} records so far")

    return all_records


# ─────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────

def run_pipeline(
    person_1_name: str,
    person_2_name: str,
) -> Dict[str, List[GenetikaRecord]]:
    """
    Run the full Geneteka search pipeline for two people.

    Args:
        person_1_name: Full name, e.g. "Jan Kowalski"
        person_2_name: Full name, e.g. "Maria Nowak"

    Returns:
        A dict  {name: [GenetikaRecord, ...]}  for each person.
    """
    print("\n" + "=" * 60)
    print("  Geneteka Genealogy Search Pipeline")
    print("=" * 60)

    results: Dict[str, List[GenetikaRecord]] = {}

    for person_name in [person_1_name, person_2_name]:
        print(f"\n▶  Searching for: {person_name}")
        t0 = time.time()
        records = search_person(person_name)
        elapsed = time.time() - t0
        results[person_name] = records
        print(f"  ✓  Found {len(records)} record(s) in {elapsed:.1f}s")

    return results


# ─────────────────────────────────────────────────────────────
# RESULT DISPLAY
# ─────────────────────────────────────────────────────────────

def display_results(results: Dict[str, List[GenetikaRecord]]) -> None:
    """Pretty-print the pipeline results to stdout."""
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)

    for person_name, records in results.items():
        print(f"\n── {person_name} ──  ({len(records)} record(s))")

        if not records:
            print("  No records found.")
            continue

        # Group by record type for readability
        by_type: Dict[str, List[GenetikaRecord]] = {}
        for r in records:
            by_type.setdefault(r.record_type, []).append(r)

        for rtype, recs in sorted(by_type.items()):
            print(f"\n  {rtype}s ({len(recs)}):")
            # Sort by year (treat missing year as "9999" for sorting)
            recs_sorted = sorted(recs, key=lambda r: r.year or "9999")
            for rec in recs_sorted:
                print(rec)


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # ── Default demo names ──────────────────────────────────
    # Change these to the names you want to search for.
    PERSON_1 = "Jan Kowalski"
    PERSON_2 = "Maria Nowak"

    # Allow overrides from command line:
    #   python geneteka_search.py "Adam Mickiewicz" "Elżbieta Mazur"
    if len(sys.argv) == 3:
        PERSON_1 = sys.argv[1]
        PERSON_2 = sys.argv[2]
    elif len(sys.argv) != 1:
        print("Usage: python geneteka_search.py [\"First1 Last1\"] [\"First2 Last2\"]")
        sys.exit(1)

    results = run_pipeline(PERSON_1, PERSON_2)
    display_results(results)
