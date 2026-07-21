"""
Vide la queue Redis "events:queue" (alimentee par api/src/events.js) vers le
Data Lake local, en Parquet, partitionne par date :

    data/events/year=YYYY/month=MM/day=DD/events_<timestamp>.parquet

Usage :
    cd data/pipeline
    python flush_events_to_parquet.py

A lancer periodiquement (cron / tache planifiee) une fois en prod. En dev,
on peut le lancer a la main pour verifier que le pipeline events -> Data Lake
fonctionne de bout en bout.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
EVENTS_QUEUE_KEY = "events:queue"

# data/pipeline/flush_events_to_parquet.py -> data/events/
DATA_DIR = Path(__file__).resolve().parent.parent
EVENTS_DIR = DATA_DIR / "events"


def pop_all_events(client):
    """Vide entierement la liste Redis de facon atomique (LPOP en batch)."""
    events = []
    while True:
        raw = client.rpop(EVENTS_QUEUE_KEY)
        if raw is None:
            break
        try:
            events.append(json.loads(raw))
        except json.JSONDecodeError:
            print(f"Event ignore (JSON invalide) : {raw[:200]}")
    return events


def partition_by_date(events):
    """Regroupe les events par (year, month, day) a partir de created_at."""
    partitions = defaultdict(list)
    for event in events:
        created_at = event.get("created_at")
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            dt = datetime.now(timezone.utc)
        key = (dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d"))
        partitions[key].append(event)
    return partitions


def write_partition(year, month, day, events):
    partition_dir = EVENTS_DIR / f"year={year}" / f"month={month}" / f"day={day}"
    partition_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(events)
    df["payload"] = df["payload"].apply(json.dumps)  # JSONB -> string pour Parquet

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    out_path = partition_dir / f"events_{timestamp}.parquet"
    df.to_parquet(out_path, engine="pyarrow", index=False)
    return out_path, len(df)


def main():
    client = redis.from_url(REDIS_URL, decode_responses=True)
    client.ping()

    events = pop_all_events(client)
    if not events:
        print("Aucun event en attente dans Redis.")
        return

    print(f"{len(events)} events recuperes depuis Redis.")

    partitions = partition_by_date(events)
    for (year, month, day), partition_events in partitions.items():
        out_path, count = write_partition(year, month, day, partition_events)
        print(f"  -> {count} events ecrits dans {out_path.relative_to(DATA_DIR.parent)}")

    print("Flush termine.")


if __name__ == "__main__":
    main()
