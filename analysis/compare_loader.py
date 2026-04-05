"""
compare_loader.py — loads both Claude and Higgsfield datasets into a
common schema for side-by-side comparison charts.
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path

PROCESSED = Path(__file__).parent.parent / "data" / "processed"
CHARTS    = Path(__file__).parent.parent / "data" / "charts"

BRAND_COLORS = {
    "Claude":     {"primary": "#e07b39", "light": "#f5c5a3", "dark": "#b85f22"},
    "Higgsfield": {"primary": "#6366f1", "light": "#a5b4fc", "dark": "#4338ca"},
}

def load_claude() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "full_dataset (1).csv", low_memory=False)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df["brand"] = "Claude"
    df["likes"]    = pd.to_numeric(df["likes"],    errors="coerce")
    df["views"]    = pd.to_numeric(df["views"],    errors="coerce")
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce")
    df["reposts"]  = pd.to_numeric(df["reposts"],  errors="coerce")
    # normalise column name
    if "title" in df.columns:
        df["post_title"] = df["title"]
    return df

def load_higgsfield() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "higgsfield_full_dataset.csv", low_memory=False)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df["brand"] = "Higgsfield"
    df["likes"]    = pd.to_numeric(df["likes"],    errors="coerce")
    df["views"]    = pd.to_numeric(df["views"],    errors="coerce")
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce")
    df["reposts"]  = pd.to_numeric(df["reposts"],  errors="coerce")
    if "title" in df.columns:
        df["post_title"] = df["title"]
    return df

def load_both() -> pd.DataFrame:
    return pd.concat([load_claude(), load_higgsfield()], ignore_index=True)
