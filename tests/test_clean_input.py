import sys
from pathlib import Path

import pandas as pd
import pytest

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ynab_import.core.clean_input import (
    clean_data_pipeline,
    delete_rows_containing_text,
    remove_header_footer,
    set_first_row_as_header,
)


class TestRemoveHeaderFooter:
    """Tests for remove_header_footer function."""

    def test_remove_header_rows_only(self) -> None:
        """Test removing only header rows."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Header 1", "Header 2"],
                ["Header 3", "Header 4"],
                ["Data 1", "Data 2"],
                ["Data 3", "Data 4"],
            ]
        )
        # Act
        result = remove_header_footer(df, header_rows=2, footer_rows=0)

        # Assert
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["Data 3", "Data 4"]
        assert result.index.tolist() == [0, 1]  # Index should be reset

    def test_remove_footer_rows_only(self) -> None:
        """Test removing only footer rows."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2"],
                ["Data 3", "Data 4"],
                ["Footer 1", "Footer 2"],
                ["Footer 3", "Footer 4"],
            ]
        )
        # Act
        result = remove_header_footer(df, header_rows=0, footer_rows=2)

        # Assert
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["Data 3", "Data 4"]
        assert result.index.tolist() == [0, 1]  # Index should be reset

    def test_remove_both_header_and_footer(self) -> None:
        """Test removing both header and footer rows."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Header 1", "Header 2"],
                ["Data 1", "Data 2"],
                ["Data 3", "Data 4"],
                ["Footer 1", "Footer 2"],
            ]
        )
        # Act
        result = remove_header_footer(df, header_rows=1, footer_rows=1)

        # Assert
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["Data 3", "Data 4"]

    def test_no_trimming(self) -> None:
        """Test with no header or footer removal."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2"],
                ["Data 3", "Data 4"],
            ]
        )
        # Act
        result = remove_header_footer(df, header_rows=0, footer_rows=0)

        # Assert
        assert len(result) == 2
        assert result.equals(df.reset_index(drop=True))

    def test_remove_all_rows(self) -> None:
        """Test edge case where header + footer >= total rows."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Row 1", "Col 2"],
                ["Row 2", "Col 2"],
            ]
        )
        # Act
        result = remove_header_footer(df, header_rows=1, footer_rows=1)

        # Assert
        assert len(result) == 0
        assert result.empty


class TestDeleteRowsContainingText:
    """Tests for delete_rows_containing_text function."""

    def test_no_text_no_removal(self) -> None:
        """Test that no rows are removed when no text is provided."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2", "Data 3"],
                ["", "", ""],
                ["Data 4", "", ""],
                ["Data 5", "Data 6", "Data 7"],
            ]
        )

        # Act
        result = delete_rows_containing_text(df)

        # Assert
        assert len(result) == 4  # All rows kept when no text provided
        assert result.iloc[0].tolist() == ["Data 1", "Data 2", "Data 3"]
        assert result.iloc[1].tolist() == ["", "", ""]
        assert result.iloc[2].tolist() == ["Data 4", "", ""]
        assert result.iloc[3].tolist() == ["Data 5", "Data 6", "Data 7"]

    def test_delete_rows_with_text(self) -> None:
        """Test deleting rows that contain specified text."""
        # Arrange
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "Total", "2023-01-02", "Summary"],
                "Amount": [100, 500, 200, 700],
                "Description": ["Purchase", "Summary", "Sale", "Total"],
            }
        )

        # Act
        result = delete_rows_containing_text(df, ["Total", "Summary"])

        # Assert
        assert len(result) == 2
        assert result.iloc[0]["Date"] == "2023-01-01"
        assert result.iloc[1]["Date"] == "2023-01-02"

    def test_delete_partial_text_match(self) -> None:
        """Test deleting rows based on partial text matching."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Date", "Amount", "Description"],
                ["2023-01-01", 100, "Purchase at Store"],
                ["2023-01-02", 200, "Sale"],
                ["Total Summary", 300, "Summary Report"],
            ]
        )

        # Act
        result = delete_rows_containing_text(df, ["Total", "Summary"])

        # Assert
        assert len(result) == 3
        assert result.iloc[0].tolist() == ["Date", "Amount", "Description"]
        assert result.iloc[1].tolist() == ["2023-01-01", 100, "Purchase at Store"]
        assert result.iloc[2].tolist() == ["2023-01-02", 200, "Sale"]

    def test_empty_text_list(self) -> None:
        """Test that empty text list doesn't remove any rows."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2"],
                ["Data 3", "Data 4"],
                ["Data 5", "Data 6"],
            ]
        )

        # Act
        result = delete_rows_containing_text(df, [])

        # Assert
        assert len(result) == 3
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["Data 3", "Data 4"]
        assert result.iloc[2].tolist() == ["Data 5", "Data 6"]

    def test_case_sensitive_matching(self) -> None:
        """Test that text matching is case sensitive."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Total"],
                ["Data 2", "total"],
                ["Data 3", "TOTAL"],
            ]
        )

        # Act
        result = delete_rows_containing_text(df, ["Total"])

        # Assert
        assert len(result) == 2  # Only exact case match should be removed
        assert result.iloc[0].tolist() == ["Data 2", "total"]
        assert result.iloc[1].tolist() == ["Data 3", "TOTAL"]

    def test_multiple_text_strings(self) -> None:
        """Test deleting rows with multiple text strings."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Keep", "This", "Row"],
                ["Remove", "This", "Row"],
                ["Keep", "This", "Too"],
                ["Delete", "This", "One"],
                ["Final", "Keep", "Row"],
            ]
        )

        # Act
        result = delete_rows_containing_text(df, ["Remove", "Delete"])

        # Assert
        assert len(result) == 3
        assert result.iloc[0].tolist() == ["Keep", "This", "Row"]
        assert result.iloc[1].tolist() == ["Keep", "This", "Too"]
        assert result.iloc[2].tolist() == ["Final", "Keep", "Row"]

    def test_numeric_values_as_strings(self) -> None:
        """Test deleting rows containing numeric values treated as strings."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Date", "Amount", "Description"],
                ["2023-01-01", 100, "Purchase"],
                ["2023-01-02", 500, "Total Payment"],
                ["2023-01-03", 200, "Sale"],
            ]
        )

        # Act - looking for "500" as text
        result = delete_rows_containing_text(df, ["500"])

        # Assert
        assert len(result) == 3  # Row with 500 should be removed
        assert result.iloc[0].tolist() == ["Date", "Amount", "Description"]
        assert result.iloc[1].tolist() == ["2023-01-01", 100, "Purchase"]
        assert result.iloc[2].tolist() == ["2023-01-03", 200, "Sale"]

    def test_empty_string_in_text_list(self) -> None:
        """Test that empty strings in text list are ignored."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2"],
                ["", ""],
                ["Data 3", "Data 4"],
                ["Remove", "This"],
            ]
        )

        # Act
        result = delete_rows_containing_text(df, ["", "Remove"])

        # Assert
        assert len(result) == 3  # Only "Remove" should cause deletion
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == [
            "",
            "",
        ]  # Empty row kept (empty string ignored)
        assert result.iloc[2].tolist() == ["Data 3", "Data 4"]


class TestSetFirstRowAsHeader:
    """Tests for set_first_row_as_header function."""

    def test_set_first_row_as_header_normal(self) -> None:
        """Test setting first row as column headers."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Date", "Amount", "Description"],
                ["2023-01-01", 100, "Purchase"],
                ["2023-01-02", 200, "Sale"],
            ]
        )

        # Act
        result = set_first_row_as_header(df)

        # Assert
        assert list(result.columns) == ["Date", "Amount", "Description"]
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["2023-01-01", 100, "Purchase"]
        assert result.iloc[1].tolist() == ["2023-01-02", 200, "Sale"]

    def test_set_first_row_as_header_with_numbers(self) -> None:
        """Test setting first row as headers when it contains numbers."""
        # Arrange
        df = pd.DataFrame(
            [
                [1, 2.5, "Text"],
                ["Data 1", "Data 2", "Data 3"],
            ]
        )

        # Act
        result = set_first_row_as_header(df)

        # Assert
        assert list(result.columns) == ["1", "2.5", "Text"]
        assert len(result) == 1
        assert result.iloc[0].tolist() == ["Data 1", "Data 2", "Data 3"]

    def test_set_first_row_as_header_empty_dataframe(self) -> None:
        """Test behavior with empty DataFrame."""
        # Arrange
        df = pd.DataFrame()

        # Act
        result = set_first_row_as_header(df)

        # Assert
        assert result.empty
        assert len(result) == 0

    def test_set_first_row_as_header_single_row(self) -> None:
        """Test behavior with single row DataFrame."""
        # Arrange
        df = pd.DataFrame([["Col1", "Col2", "Col3"]])

        # Act
        result = set_first_row_as_header(df)

        # Assert
        assert list(result.columns) == ["Col1", "Col2", "Col3"]
        assert len(result) == 0  # No data rows left


class TestCleanDataPipeline:
    """Tests for clean_data_pipeline function."""

    def test_full_pipeline_with_all_options(self) -> None:
        """Test complete cleaning pipeline with all options enabled."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Ignore", "This", "Header"],  # Header to remove
                ["Date", "Amount", "Description"],  # Will become column headers
                ["2023-01-01", 100, "Purchase"],
                ["", "", ""],  # Empty row to keep
                ["Total", 500, "Summary"],  # Row to delete via text matching
                ["2023-01-02", 200, "Sale"],
                ["Footer", "Row", "Ignore"],  # Footer to remove
            ]
        )

        # Act
        result = clean_data_pipeline(
            df,
            header_rows=1,
            footer_rows=1,
            del_rows_with=["Total"],
            set_header=True,
        )

        # Assert
        assert list(result.columns) == ["Date", "Amount", "Description"]
        assert len(result) == 3  # Empty row kept, Total row removed
        assert result.iloc[0]["Date"] == "2023-01-01"
        assert result.iloc[0]["Amount"] == 100
        assert result.iloc[1]["Date"] == ""  # Empty row kept
        assert result.iloc[2]["Date"] == "2023-01-02"
        assert result.iloc[2]["Amount"] == 200

    def test_pipeline_with_trim_only(self) -> None:
        """Test pipeline with only header/footer trimming."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Header", "Row"],
                ["Data 1", "Data 2"],
                ["Data 3", "Data 4"],
                ["Footer", "Row"],
            ]
        )

        # Act
        result = clean_data_pipeline(df, header_rows=1, footer_rows=1)

        # Assert
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["Data 3", "Data 4"]

    def test_pipeline_with_text_deletion_only(self) -> None:
        """Test pipeline with only text-based row deletion."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2"],
                ["Skip", "This"],
                ["Data 3", "Data 4"],
            ]
        )

        # Act
        result = clean_data_pipeline(df, del_rows_with=["Skip"])

        # Assert
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["Data 3", "Data 4"]

    def test_pipeline_with_set_header_only(self) -> None:
        """Test pipeline with only header setting."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Col1", "Col2", "Col3"],
                ["Data 1", "Data 2", "Data 3"],
            ]
        )

        # Act
        result = clean_data_pipeline(df, set_header=True)

        # Assert
        assert list(result.columns) == ["Col1", "Col2", "Col3"]
        assert len(result) == 1
        assert result.iloc[0].tolist() == ["Data 1", "Data 2", "Data 3"]

    def test_pipeline_no_operations(self) -> None:
        """Test pipeline with no operations."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2"],
                ["", ""],
                ["Data 3", "Data 4"],
            ]
        )

        # Act
        result = clean_data_pipeline(df)

        # Assert
        assert len(result) == 3  # All rows kept when no operations
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["", ""]
        assert result.iloc[2].tolist() == ["Data 3", "Data 4"]

    def test_pipeline_with_multiple_text_deletions(self) -> None:
        """Test pipeline with multiple text deletion criteria."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data 1", "Data 2"],
                ["Skip Me", "Value"],  # Should be removed
                ["Data 3", "Data 4"],
                ["Remove This", "Too"],  # Should be removed
                ["Data 5", "Data 6"],
            ]
        )

        # Act
        result = clean_data_pipeline(df, del_rows_with=["Skip Me", "Remove This"])

        # Assert
        assert len(result) == 3
        assert result.iloc[0].tolist() == ["Data 1", "Data 2"]
        assert result.iloc[1].tolist() == ["Data 3", "Data 4"]
        assert result.iloc[2].tolist() == ["Data 5", "Data 6"]

    def test_pipeline_preserves_original_data(self) -> None:
        """Test that pipeline doesn't modify original DataFrame."""
        # Arrange
        original_data = [
            ["Header"],
            ["Data 1"],
            ["Data 2"],
        ]
        df = pd.DataFrame(original_data)
        original_df = df.copy()

        # Act
        _ = clean_data_pipeline(df, header_rows=1)

        # Assert
        assert df.equals(original_df)  # Original should be unchanged


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_dataframe(self) -> None:
        """Test behavior with empty DataFrame."""
        # Arrange
        df = pd.DataFrame()

        # Act
        result = clean_data_pipeline(df, header_rows=1, del_rows_with=["test"])

        # Assert
        assert result.empty
        assert len(result) == 0

    def test_none_values_in_dataframe(self) -> None:
        """Test handling of None values in DataFrame."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Data", None, "Test"],
                [None, "Remove", "This"],
                ["Keep", "This", None],
            ]
        )

        # Act
        result = delete_rows_containing_text(df, ["Remove"])

        # Assert
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["Data", None, "Test"]
        assert result.iloc[1].tolist() == ["Keep", "This", None]


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests with realistic bank data scenarios."""

    def test_norwegian_bank_csv_cleaning(self) -> None:
        """Test cleaning typical Norwegian bank CSV data."""
        # Arrange - simulate Norwegian bank CSV structure
        df = pd.DataFrame(
            [
                ["Kontoutskrift", "", "", ""],  # Header to remove
                ["Dato", "Beløp", "Tekst", "Type"],  # Column headers
                ["2023-01-01", "-100.50", "REMA 1000", "Betaling"],
                ["", "", "", ""],  # Empty row
                ["Totalt beløp:", "1500.00", "", ""],  # Summary row to skip
                ["2023-01-02", "2500.00", "Lønn", "Innskudd"],
                ["", "Slutt på utskrift", "", ""],  # Footer to remove
            ]
        )

        # Act
        result = clean_data_pipeline(
            df,
            header_rows=1,
            footer_rows=1,
            del_rows_with=["Totalt beløp:"],
            set_header=True,
        )

        # Assert
        assert list(result.columns) == ["Dato", "Beløp", "Tekst", "Type"]
        assert len(result) == 3  # Empty rows kept, summary row removed
        assert result.iloc[0]["Dato"] == "2023-01-01"
        assert result.iloc[0]["Beløp"] == "-100.50"
        assert result.iloc[1]["Dato"] == ""  # Empty row kept
        assert result.iloc[2]["Dato"] == "2023-01-02"
        assert result.iloc[2]["Beløp"] == "2500.00"

    def test_credit_card_statement_cleaning(self) -> None:
        """Test cleaning typical credit card statement."""
        # Arrange - simulate credit card statement
        df = pd.DataFrame(
            [
                ["Account Summary", "Period: Jan 2023", "", ""],
                ["", "", "", ""],
                ["Date", "Description", "Amount", "Balance"],
                ["2023-01-15", "AMAZON.COM", "-89.99", "1500.00"],
                ["", "", "", ""],  # Empty transaction row
                ["2023-01-16", "PAYMENT - THANK YOU", "500.00", "2000.00"],
                ["TOTAL PURCHASES", "-89.99", "", ""],  # Summary to skip
                ["TOTAL PAYMENTS", "500.00", "", ""],  # Summary to skip
            ]
        )

        # Act
        result = clean_data_pipeline(
            df,
            header_rows=2,
            footer_rows=0,
            del_rows_with=["TOTAL PURCHASES", "TOTAL PAYMENTS"],
            set_header=True,
        )

        # Assert
        assert list(result.columns) == ["Date", "Description", "Amount", "Balance"]
        assert len(result) == 3  # Empty row kept, summary rows removed
        assert result.iloc[0]["Description"] == "AMAZON.COM"
        assert result.iloc[1]["Description"] == ""  # Empty row kept
        assert result.iloc[2]["Description"] == "PAYMENT - THANK YOU"


class TestCleanDataWithPreset:
    """Tests for clean_data_with_preset function."""

    def test_clean_data_with_preset_basic(self) -> None:
        """Test basic cleaning using preset configuration."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Header", "Row"],
                ["Date", "Amount"],
                ["2023-01-01", 100],
                ["Total", 500],
                ["2023-01-02", 200],
                ["Footer", "Row"],
            ]
        )

        # Create a mock preset object with the required attributes
        class MockPreset:
            def __init__(self):
                self.header_skiprows = 1
                self.footer_skiprows = 1
                self.del_rows_with = ["Total"]

        preset = MockPreset()

        # Act
        from ynab_import.core.clean_input import clean_data_with_preset

        result = clean_data_with_preset(df, preset, set_header=True)

        # Assert
        assert list(result.columns) == ["Date", "Amount"]
        assert len(result) == 2  # Total row removed, others kept
        assert result.iloc[0]["Date"] == "2023-01-01"
        assert result.iloc[0]["Amount"] == 100
        assert result.iloc[1]["Date"] == "2023-01-02"
        assert result.iloc[1]["Amount"] == 200

    def test_clean_data_with_preset_no_header_setting(self) -> None:
        """Test cleaning with preset but without setting headers."""
        # Arrange
        df = pd.DataFrame(
            [
                ["Remove", "This"],
                ["Keep", "This"],
                ["Remove", "Too"],
                ["Keep", "Also"],
            ]
        )

        class MockPreset:
            def __init__(self):
                self.header_skiprows = 0
                self.footer_skiprows = 0
                self.del_rows_with = ["Remove"]

        preset = MockPreset()

        # Act
        from ynab_import.core.clean_input import clean_data_with_preset

        result = clean_data_with_preset(df, preset, set_header=False)

        # Assert
        assert len(result) == 2
        assert result.iloc[0].tolist() == ["Keep", "This"]
        assert result.iloc[1].tolist() == ["Keep", "Also"]
