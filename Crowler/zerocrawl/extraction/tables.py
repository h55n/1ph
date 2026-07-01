"""
ZeroCrawl — Table Extraction
Converts HTML tables to list-of-dict arrays with correct headers.
"""
from __future__ import annotations

from typing import Any

try:
    from selectolax.parser import HTMLParser, Node
    _SL = True
except ImportError:
    _SL = False


def _get_cell_text(node) -> str:
    try:
        return (node.text(strip=True) or "").strip()
    except Exception:
        return ""


def _expand_rowspan_colspan(raw_rows: list[list[str]]) -> list[list[str]]:
    """
    Expand a matrix of raw cells that may have been collected
    without regard for rowspan/colspan into a rectangular matrix.
    This is a simplification — selectolax doesn't expose span attributes
    directly in the same way, so we work with what we have.
    """
    return raw_rows


def extract_tables(raw_html: str) -> list[list[dict[str, Any]]]:
    """
    Extract all HTML tables as list of row dicts.
    Returns list of tables, each table is a list of row dicts.
    """
    if not raw_html or not _SL:
        return []

    try:
        tree = HTMLParser(raw_html)
    except Exception:
        return []

    tables = []

    for table_node in tree.css("table"):
        rows_data = _parse_table(table_node)
        if rows_data:
            tables.append(rows_data)

    return tables


def _parse_table(table_node) -> list[dict[str, Any]]:
    """Parse a single table node into list of row dicts."""
    # Collect all rows
    raw_rows: list[list[str]] = []
    header_row: list[str] = []
    is_first_row_header = False

    # Try <thead><tr><th> first
    thead = table_node.css_first("thead")
    if thead:
        th_row = thead.css_first("tr")
        if th_row:
            headers = [_get_cell_text(th) for th in th_row.css("th, td")]
            if headers:
                header_row = headers
                is_first_row_header = True

    # Collect body rows
    tbody = table_node.css_first("tbody") or table_node
    for tr in tbody.css("tr"):
        row = [_get_cell_text(td) for td in tr.css("td, th")]
        if row:
            raw_rows.append(row)

    if not raw_rows:
        return []

    # If no explicit header was found, check if first row is all <th>
    if not is_first_row_header and raw_rows:
        first_tr = table_node.css("tr")
        if first_tr:
            first_cells = first_tr[0].css("th")
            if len(first_cells) == len(raw_rows[0]):
                header_row = raw_rows[0]
                raw_rows = raw_rows[1:]
                is_first_row_header = True

    # If still no header, use column indices
    if not header_row:
        if raw_rows:
            max_cols = max(len(r) for r in raw_rows)
            header_row = [f"column_{i+1}" for i in range(max_cols)]

    # Build list of dicts
    result = []
    for row in raw_rows:
        row_dict: dict[str, Any] = {}
        for i, cell in enumerate(row):
            if i < len(header_row):
                key = header_row[i] or f"column_{i+1}"
            else:
                key = f"column_{i+1}"
            row_dict[key] = cell
        if any(v.strip() for v in row_dict.values()):
            result.append(row_dict)

    return result
