from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import pytest

from ynab_import.core.diagnostics import ConversionError
from ynab_import.core.pipeline import convert_file_with_preset, preview_conversion
from ynab_import.core.preset import Preset


class TestPipelineDiagnostics:
    def test_preview_conversion_wraps_amount_parse_errors(self) -> None:
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-01"],
                "Amount": ["12-34"],
                "Description": ["Broken"],
            }
        )

        preset = Preset(
            name="broken",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Outflow": "Amount",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        with pytest.raises(ConversionError) as exc_info:
            preview_conversion(input_df, preset)

        error = exc_info.value
        assert error.stage == "convert"
        assert error.preset_name == "broken"
        assert "Amount" in error.columns

    def test_auto_header_detection_falls_back_with_warning(
        self, tmp_path: Path
    ) -> None:
        input_df = pd.DataFrame(
            [
                ["Unexpected", "Export", "Format"],
                ["Still", "Not", "Headers"],
                ["Date", "Description", "Amount"],
                ["2024-01-01", "Store", "-45.67"],
            ]
        )
        input_path = tmp_path / "transactions.xlsx"
        input_df.to_excel(input_path, index=False, header=False)  # type: ignore[reportUnknownMemberType]

        preset = Preset(
            name="auto",
            column_mappings={
                "Date": "Missing Date Header",
                "Payee": "Missing Description Header",
                "Outflow": "Missing Amount Header",
            },
            header_skiprows=1,
            footer_skiprows=0,
            del_rows_with=[],
            header_mode="auto",
        )

        output_dir = tmp_path / "out"
        output_dir.mkdir()

        result = convert_file_with_preset(input_path, preset, output_dir, "auto")

        assert len(result.warnings) == 1
        assert "Falling back" in result.warnings[0].message

    def test_auto_header_detection_uses_detected_header(self) -> None:
        input_df = pd.DataFrame(
            [
                ["Ignore", "", ""],
                ["Date", "Description", "Amount"],
                ["2024-01-01", "Store", "-45.67"],
            ]
        )

        preset = Preset(
            name="auto",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Outflow": "Amount",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
            header_mode="auto",
        )

        preview_result = preview_conversion(input_df, preset)

        assert preview_result.warnings == []
        assert list(preview_result.data.columns) == ["Date", "Payee", "Outflow"]
        assert preview_result.data.iloc[0]["Payee"] == "Store"
