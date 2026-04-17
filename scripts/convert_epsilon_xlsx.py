"""
Convert Epsilon TSP Data Dictionary Excel to a filtered CSV.

Usage: python scripts/convert_epsilon_xlsx.py [path/to/epsilon.xlsx]
Output: data/epsilon_taxonomy.csv

Keeps only rows with a non-null Value (actual segments) and excludes
non-targeting dimensions (Name & Address, Record Filter, Geography).
"""

import sys
import pandas as pd
from pathlib import Path

EXCLUDE_DIMENSIONS = {"Name & Address", "Record Filter", "Geography"}

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/atif/Downloads/ARI TSP_Data_Dictionary_ARI_Ready.xlsx"
)
dst = Path(__file__).resolve().parent.parent / "data" / "epsilon_taxonomy.csv"

print(f"Reading: {src}")
df = pd.read_excel(src, sheet_name="🗂 Master (All Data)")
print(f"Total rows: {len(df)}")

df = df[df["Value"].notna() & (df["Value"] != "")]
df = df[~df["Dimension"].isin(EXCLUDE_DIMENSIONS)]
# Drop copyright/footer rows
df = df[~df["Category"].str.contains("©|Epsilon Data Management", case=False, na=False)]

print(f"Filtered rows: {len(df)}")
print(f"Dimensions: {sorted(df['Dimension'].unique())}")

dst.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(dst, index=False)
print(f"Written to: {dst}")
