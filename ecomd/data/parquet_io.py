"""Parquet helpers that read one physical file without Hive partition inference."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pandas as pd
import pyarrow.parquet as pq


def read_single_parquet(path: Path) -> pd.DataFrame:
    """Read exactly ``path``, ignoring partition keys encoded by parent folders."""
    table = pq.ParquetFile(path).read()  # type: ignore[no-untyped-call]
    return cast(pd.DataFrame, table.to_pandas())


__all__ = ["read_single_parquet"]
