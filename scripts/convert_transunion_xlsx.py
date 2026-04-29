"""
Convert TransUnion TruAudience AdAdvisor Taxonomy Excel to a clean CSV.

Usage: python scripts/convert_transunion_xlsx.py [path/to/transunion.xlsx]
Output: data/transunion_taxonomy.csv

Strips the redundant "AdAdvisor by TransUnion > " prefix from every Audience Name.
"""

import sys
import pandas as pd
from pathlib import Path

PREFIX = "AdAdvisor by TransUnion > "

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/atif/Downloads/TruAudience AdAdvisor Taxonomy.12.4.25.xlsx"
)
dst = Path(__file__).resolve().parent.parent / "data" / "transunion_taxonomy.csv"

print(f"Reading: {src}")
df = pd.read_excel(
    src,
    sheet_name="TruAudience AdAdvisor Taxonomy",
    header=12,
)
print(f"Total rows: {len(df)}")

# Trim whitespace and rename
df = df.rename(columns={c: c.strip() if isinstance(c, str) else c for c in df.columns})

# Keep only the columns we need
keep = ["Category", "Audience Name", "Description"]
df = df[[c for c in keep if c in df.columns]]

# Drop rows missing Category or Audience Name
df = df.dropna(subset=["Category", "Audience Name"])

# Strip the redundant TransUnion prefix
df["Audience Name"] = df["Audience Name"].astype(str).str.replace(
    PREFIX, "", regex=False
)

print(f"Filtered rows: {len(df)}")
print(f"Categories: {sorted(df['Category'].unique())}")

dst.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(dst, index=False)
print(f"Written to: {dst}")
