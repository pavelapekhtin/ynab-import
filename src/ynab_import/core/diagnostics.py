from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from pandas import DataFrame


def sanitize_scalar(value: Any) -> str:
    if pd.isna(value):
        return ""

    text = str(value)
    sanitized = "".join(char for char in text if char == "\n" or 32 <= ord(char) <= 126)
    sanitized = sanitized.replace("\r", " ").replace("\t", " ").replace("\n", " ")
    return " ".join(sanitized.split())


def dataframe_excerpt(
    df: DataFrame, columns: list[str] | None = None, max_rows: int = 5
) -> list[dict[str, str]]:
    excerpt_df = df.copy()
    if columns:
        selected = [column for column in columns if column in excerpt_df.columns]
        if selected:
            excerpt_df = excerpt_df[selected]

    rows: list[dict[str, str]] = []
    for _, row in excerpt_df.head(max_rows).iterrows():
        rows.append(
            {str(column): sanitize_scalar(value) for column, value in row.items()}
        )
    return rows


@dataclass
class ConversionWarning:
    message: str
    stage: str | None = None


@dataclass
class ConversionError(Exception):
    stage: str
    summary: str
    expected: str
    actual: str
    columns: list[str] = field(default_factory=list)
    excerpt: list[dict[str, str]] = field(default_factory=list)
    preset_name: str | None = None

    def __str__(self) -> str:
        return self.summary


@dataclass
class ConversionResult:
    output_path: Path
    warnings: list[ConversionWarning] = field(default_factory=list)


@dataclass
class PreviewResult:
    data: DataFrame
    warnings: list[ConversionWarning] = field(default_factory=list)
