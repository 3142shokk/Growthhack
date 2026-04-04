import csv
import json
import os
from datetime import datetime

from models.post import Post


def export_csv(posts: list[Post], path: str) -> None:
    if not posts:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = [p.to_csv_row() for p in posts]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(posts)} posts → {path}")


def export_json(posts: list[Post], path: str) -> None:
    if not posts:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = [p.model_dump(mode="json") for p in posts]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Exported {len(posts)} posts → {path}")


def export_raw(raw: list[dict], platform: str, raw_dir: str) -> None:
    os.makedirs(raw_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(raw_dir, f"{platform}_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, default=str)
    print(f"Raw data saved → {path}")
