"""
Convert Aristotle Digital Taxonomy Excel to a clean CSV.

Usage: python scripts/convert_aristotle_xlsx.py [path/to/aristotle.xlsx]
Output: data/aristotle_taxonomy.csv

Combines 9 marketing sheets + "Top Segments" + "Mobile & Cookie Reach" into a
single normalized CSV with columns: Sheet, Category, Segment, Description,
Data Dictionary Naming.
"""

import sys
import re
import pandas as pd
from pathlib import Path

# Sheet name → simplified dimension label
MARKETING_SHEETS = {
    "Aristotle Consumer Marketing":   "Consumer",
    "Aristotle Political Marketing":  "Political",
    "Aristotle Government Marketing": "Government",
    "Aristotle Affluent Marketing":   "Affluent",
    "Aristotle Medical Marketing":    "Medical",
    "Aristotle Auto Marketing":       "Auto",
    "Aristotle Holiday Marketing":    "Holiday",
    "Aristotle Business Marketing":   "Business",
    "Education & Alumni":             "Education",
}


def _normalize_str(v):
    if pd.isna(v):
        return ""
    return str(v).strip()


def load_marketing_sheet(xl: pd.ExcelFile, sheet_name: str, dimension: str) -> pd.DataFrame:
    """Read a marketing sheet (header at row 3) and normalize column names."""
    df = pd.read_excel(xl, sheet_name=sheet_name, header=3)
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    # Required columns
    df = df.dropna(subset=["Category", "Segment"])
    # Filter out replica header rows
    df = df[
        ~(df["Category"].astype(str).str.strip().str.lower() == "category")
        & ~(df["Segment"].astype(str).str.strip().str.lower() == "segment")
    ]
    out = pd.DataFrame({
        "Sheet": dimension,
        "Category": df["Category"].apply(_normalize_str),
        "Segment": df["Segment"].apply(_normalize_str),
        "Description": df.get("Description of Segment", "").apply(_normalize_str),
        "Data Dictionary Naming": df.get("Data Dictionary Naming", "").apply(_normalize_str),
    })
    return out


def load_top_segments(xl: pd.ExcelFile) -> pd.DataFrame:
    """Read the curated 'Top Segments' sheet. Sub-section header rows (where
    only column 0 is set with an uppercase phrase like 'POLITICAL SEGMENTS')
    carry the sub-category for following rows."""
    df = pd.read_excel(xl, sheet_name="Top Segments", header=1)
    df.columns = ["Segment", "Description", "Data Dictionary Naming"]

    current_subcat = "General"
    rows = []
    for _, r in df.iterrows():
        seg = _normalize_str(r["Segment"])
        desc = _normalize_str(r["Description"])
        ddn = _normalize_str(r["Data Dictionary Naming"])
        if not seg:
            continue
        # Sub-section marker: only Segment column populated, all-caps
        if seg.endswith("SEGMENTS") and not desc and not ddn:
            current_subcat = seg.replace(" SEGMENTS", "").title()
            continue
        # Also skip the header row itself
        if seg.lower() == "segment name" or seg.lower() == "description of segment":
            continue
        rows.append({
            "Sheet": "Top Segments",
            "Category": current_subcat,
            "Segment": seg,
            "Description": desc,
            "Data Dictionary Naming": ddn,
        })
    return pd.DataFrame(rows)


def load_mobile_cookie_reach(xl: pd.ExcelFile) -> pd.DataFrame:
    """Read 'Aristotle Mobile & Cookie Reach' sheet. Segment Name is a
    '>'-delimited path like 'Aristotle > Affluent > Lifestyle & Interests > Collectors - Art'."""
    df = pd.read_excel(xl, sheet_name="Aristotle Mobile & Cookie Reach", header=0)
    df.columns = ["Segment Name", "Cookie Reach", "IOS Reach", "Android Reach"]

    rows = []
    for _, r in df.iterrows():
        path = _normalize_str(r["Segment Name"])
        if not path or path.lower() == "segment name":
            continue
        parts = [p.strip() for p in path.split(" > ") if p.strip()]
        if len(parts) < 3:
            continue
        # parts[0] usually "Aristotle"; parts[1] dimension; parts[2..n-1] category; parts[-1] leaf
        dimension = parts[1] if parts[0].lower() == "aristotle" else parts[0]
        leaf = parts[-1]
        category = " > ".join(parts[2:-1]) if len(parts) > 3 else (parts[2] if len(parts) == 3 else "")
        rows.append({
            "Sheet": "Mobile & Cookie Reach",
            "Category": f"{dimension} > {category}" if category else dimension,
            "Segment": leaf,
            "Description": "",
            "Data Dictionary Naming": "",
        })
    return pd.DataFrame(rows)


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/Users/atif/Downloads/Aristotle Digital Taxonomy 2026 (CONFIDENTIAL).xlsx"
    )
    dst = Path(__file__).resolve().parent.parent / "data" / "aristotle_taxonomy.csv"

    print(f"Reading: {src}")
    xl = pd.ExcelFile(src)

    parts = []
    for sheet_name, dimension in MARKETING_SHEETS.items():
        if sheet_name not in xl.sheet_names:
            print(f"  WARN: sheet {sheet_name!r} not found, skipping")
            continue
        part = load_marketing_sheet(xl, sheet_name, dimension)
        print(f"  {sheet_name}: {len(part)} rows -> dim={dimension}")
        parts.append(part)

    if "Top Segments" in xl.sheet_names:
        top = load_top_segments(xl)
        print(f"  Top Segments: {len(top)} rows")
        parts.append(top)

    if "Aristotle Mobile & Cookie Reach" in xl.sheet_names:
        mcr = load_mobile_cookie_reach(xl)
        print(f"  Mobile & Cookie Reach: {len(mcr)} rows")
        parts.append(mcr)

    combined = pd.concat(parts, ignore_index=True)
    # Drop fully-empty rows
    combined = combined[combined["Segment"].astype(str).str.strip().astype(bool)]
    print(f"Total rows: {len(combined)}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(dst, index=False)
    print(f"Written to: {dst}")


if __name__ == "__main__":
    main()
