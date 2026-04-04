"""
JSONL writer with file rotation and thread-safe queue.

- Append-only JSONL format (one JSON object per line)
- Rotates files every N tweets (default 50,000)
- Single writer consumes from a queue (no race conditions)
- Flush after every write for crash safety
"""

from __future__ import annotations

import json
import logging
import os
import threading
from queue import Empty, Queue
from typing import Optional

logger = logging.getLogger(__name__)


class JSONWriter:
    def __init__(
        self,
        output_dir: str = "data/x_tweets",
        max_per_file: int = 50_000,
        prefix: str = "tweets",
    ):
        self.output_dir = output_dir
        self.max_per_file = max_per_file
        self.prefix = prefix
        self._queue: Queue[Optional[dict]] = Queue()
        self._file = None
        self._file_index = 1
        self._file_count = 0
        self._total_written = 0
        self._thread: Optional[threading.Thread] = None
        self._running = False

        os.makedirs(output_dir, exist_ok=True)

        # Find the next file index (for resume)
        existing = [
            f for f in os.listdir(output_dir)
            if f.startswith(prefix) and f.endswith(".jsonl")
        ]
        if existing:
            nums = []
            for f in existing:
                try:
                    n = int(f.replace(prefix + "_", "").replace(".jsonl", ""))
                    nums.append(n)
                except ValueError:
                    pass
            if nums:
                self._file_index = max(nums)
                # Count lines in the last file
                last_file = os.path.join(output_dir, f"{prefix}_{self._file_index:04d}.jsonl")
                if os.path.exists(last_file):
                    with open(last_file, "r", encoding="utf-8") as f:
                        self._file_count = sum(1 for _ in f)
                    if self._file_count >= max_per_file:
                        self._file_index += 1
                        self._file_count = 0

    @property
    def total_written(self) -> int:
        return self._total_written

    def _current_path(self) -> str:
        return os.path.join(
            self.output_dir, f"{self.prefix}_{self._file_index:04d}.jsonl"
        )

    def _ensure_file(self) -> None:
        if self._file is None or self._file_count >= self.max_per_file:
            if self._file:
                self._file.close()
                logger.info(
                    f"[writer] Rotated: {self.prefix}_{self._file_index:04d}.jsonl "
                    f"({self._file_count} tweets)"
                )
                self._file_index += 1
                self._file_count = 0
            self._file = open(self._current_path(), "a", encoding="utf-8")

    def start(self) -> None:
        """Start the background writer thread."""
        self._running = True
        self._thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._thread.start()
        logger.info(f"[writer] Started, output: {self.output_dir}/")

    def stop(self) -> None:
        """Signal the writer to stop and wait for queue to drain."""
        self._queue.put(None)  # poison pill
        if self._thread:
            self._thread.join(timeout=30)
        if self._file:
            self._file.close()
            self._file = None
        self._running = False
        logger.info(f"[writer] Stopped. Total written: {self._total_written:,}")

    def write(self, tweet: dict) -> None:
        """Add a tweet to the write queue."""
        self._queue.put(tweet)

    def write_batch(self, tweets: list[dict]) -> None:
        """Add multiple tweets to the write queue."""
        for t in tweets:
            self._queue.put(t)

    def _writer_loop(self) -> None:
        """Background loop that consumes from queue and writes to disk."""
        while self._running:
            try:
                tweet = self._queue.get(timeout=1)
            except Empty:
                continue

            if tweet is None:  # poison pill
                break

            self._ensure_file()
            line = json.dumps(tweet, ensure_ascii=False, default=str)
            self._file.write(line + "\n")
            self._file.flush()
            self._file_count += 1
            self._total_written += 1

            if self._total_written % 10_000 == 0:
                logger.info(
                    f"[writer] Progress: {self._total_written:,} tweets written, "
                    f"file {self._file_index:04d} ({self._file_count}/{self.max_per_file})"
                )

    def write_sync(self, tweet: dict) -> None:
        """Write a tweet synchronously (no background thread needed)."""
        self._ensure_file()
        line = json.dumps(tweet, ensure_ascii=False, default=str)
        self._file.write(line + "\n")
        self._file.flush()
        self._file_count += 1
        self._total_written += 1

    def close(self) -> None:
        """Close file handle (for sync mode)."""
        if self._file:
            self._file.close()
            self._file = None
