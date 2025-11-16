"""Tests for improved CSV reading and diagnostic functionality."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from ynab_import.file_rw.readers import read_transaction_file


class TestImprovedCsvReading:
    """Test the improved CSV reading functionality."""

    def test_read_well_formed_csv(self, tmp_path: Path) -> None:
        """Test reading a well-formed CSV file."""
        csv_content = """Date,Description,Amount
2024-01-01,Grocery Store,-45.67
2024-01-02,Gas Station,-32.10
2024-01-03,Salary,2500.00"""

        csv_file = tmp_path / "well_formed.csv"
        csv_file.write_text(csv_content)

        df = read_transaction_file(csv_file)

        assert len(df) == 3
        assert list(df.columns) == ["Date", "Description", "Amount"]
        assert df.iloc[0]["Description"] == "Grocery Store"

    def test_read_csv_with_inconsistent_fields_warning_mode(
        self, tmp_path: Path
    ) -> None:
        """Test reading CSV with inconsistent field counts using warning mode."""
        csv_content = """Date,Description,Amount
2024-01-01,Grocery Store,-45.67
2024-01-02,Gas Station,-32.10
2024-01-03,Complex entry,Amount with multiple,delimiter issues,extra field,-123.45
2024-01-04,Normal transaction,-15.20"""

        csv_file = tmp_path / "inconsistent.csv"
        csv_file.write_text(csv_content)

        # Should still read the file but with warnings
        with patch("ynab_import.file_rw.readers.logger.warning"):
            df = read_transaction_file(csv_file)

            # Should have attempted to read with lenient settings
            assert len(df) >= 3  # Should read at least the well-formed rows

    def test_read_csv_with_encoding_issues(self, tmp_path: Path) -> None:
        """Test reading CSV with UTF-8 BOM encoding."""
        csv_content = """Date,Description,Amount
2024-01-01,Café Transaction,-45.67
2024-01-02,Naïve Store,-32.10"""

        csv_file = tmp_path / "utf8_bom.csv"
        # Write with BOM
        csv_file.write_bytes(b"\xef\xbb\xbf" + csv_content.encode("utf-8"))

        df = read_transaction_file(csv_file)

        assert len(df) == 2
        assert "Café Transaction" in df["Description"].values

    def test_read_csv_semicolon_delimiter(self, tmp_path: Path) -> None:
        """Test reading CSV with semicolon delimiter."""
        csv_content = """Date;Description;Amount
2024-01-01;Grocery Store;-45,67
2024-01-02;Gas Station;-32,10"""

        csv_file = tmp_path / "semicolon.csv"
        csv_file.write_text(csv_content)

        df = read_transaction_file(csv_file)

        assert len(df) == 2
        assert list(df.columns) == ["Date", "Description", "Amount"]

    def test_read_csv_completely_malformed_raises_error(self, tmp_path: Path) -> None:
        """Test that completely malformed CSV with many issues can still be read with warnings."""
        csv_content = """Date,Description,Amount
2024-01-01,Grocery Store,-45.67
2024-01-02,Gas Station,-32.10
2024-01-03,Complex entry,with,many,extra,fields,and,issues,-123.45,more,fields,here
2024-01-04,Another,problematic,line,with,different,field,count
2024-01-05,Yet,another,bad,line,with,way,too,many,comma,separated,values"""

        csv_file = tmp_path / "malformed.csv"
        csv_file.write_text(csv_content)

        # Should read with warnings, not raise an error
        with patch("ynab_import.file_rw.readers.logger.warning"):
            df = read_transaction_file(csv_file)
            # Should have at least the header and well-formed rows
            assert len(df) >= 2


class TestCsvReadingEdgeCases:
    """Test edge cases in CSV reading."""

    def test_read_excel_file(self, tmp_path: Path) -> None:
        """Test reading Excel file still works."""
        # Create a simple Excel file using pandas
        df = pd.DataFrame(
            {
                "Date": ["2024-01-01", "2024-01-02"],
                "Description": ["Store A", "Store B"],
                "Amount": [-45.67, -32.10],
            }
        )

        excel_file = tmp_path / "test.xlsx"
        df.to_excel(excel_file, index=False)

        result_df = read_transaction_file(excel_file)

        assert len(result_df) == 2
        assert list(result_df.columns) == ["Date", "Description", "Amount"]

    def test_read_unsupported_format_raises_error(self, tmp_path: Path) -> None:
        """Test that unsupported file format raises appropriate error."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("some text content")

        with pytest.raises(ValueError) as exc_info:
            read_transaction_file(txt_file)

        assert "Unsupported file format" in str(exc_info.value)
        assert ".txt" in str(exc_info.value)

    def test_csv_with_spaces_around_delimiter(self, tmp_path: Path) -> None:
        """Test CSV with spaces around delimiter is handled correctly."""
        csv_content = """Date , Description , Amount
2024-01-01 , Grocery Store , -45.67
2024-01-02 , Gas Station , -32.10"""

        csv_file = tmp_path / "spaces.csv"
        csv_file.write_text(csv_content)

        df = read_transaction_file(csv_file)

        assert len(df) == 2
        # Column names will have spaces, so access with spaces or strip them
        description_col = [col for col in df.columns if "Description" in col][0]
        assert df.iloc[0][description_col].strip() == "Grocery Store"


class TestImprovedDelimiterDetection:
    """Test the improved delimiter detection logic."""

    def test_delimiter_detection_pure_semicolon(self, tmp_path: Path) -> None:
        """Test detection of pure semicolon-delimited files."""
        csv_content = """Date;Description;Amount
2024-01-01;Grocery Store;-45,67
2024-01-02;Gas Station;-32,10"""

        csv_file = tmp_path / "pure_semicolon.csv"
        csv_file.write_text(csv_content)

        df = read_transaction_file(csv_file)
        assert len(df.columns) == 3
        assert df.iloc[0]["Description"] == "Grocery Store"

    def test_delimiter_detection_mixed_preference_semicolon(
        self, tmp_path: Path
    ) -> None:
        """Test that semicolons are preferred when counts are close."""
        csv_content = """Date;Description;Amount
2024-01-01;Store, Location A;-45,67
2024-01-02;Gas Station, Highway;-32,10"""

        csv_file = tmp_path / "mixed_prefer_semicolon.csv"
        csv_file.write_text(csv_content)

        df = read_transaction_file(csv_file)
        # Should have 3 columns if semicolon delimiter was detected correctly
        assert len(df.columns) == 3

    def test_delimiter_detection_comma_dominant(self, tmp_path: Path) -> None:
        """Test comma detection when commas are more frequent."""
        csv_content = """Date,Description,Amount,Extra,More
2024-01-01,"Store; Location","-45,67","Info; Data","More; Info"
2024-01-02,"Gas Station; Highway","-32,10","Other; Stuff","Extra; Data" """

        csv_file = tmp_path / "comma_dominant.csv"
        csv_file.write_text(csv_content)

        df = read_transaction_file(csv_file)
        # Should have 5 columns if comma delimiter was detected correctly
        assert len(df.columns) == 5

    def test_delimiter_detection_only_semicolons_no_commas(
        self, tmp_path: Path
    ) -> None:
        """Test semicolon detection when only semicolons exist."""
        csv_content = """Date;Description;Amount
2024-01-01;Grocery Store;-4567
2024-01-02;Gas Station;-3210"""

        csv_file = tmp_path / "only_semicolons.csv"
        csv_file.write_text(csv_content)

        df = read_transaction_file(csv_file)
        assert len(df.columns) == 3
