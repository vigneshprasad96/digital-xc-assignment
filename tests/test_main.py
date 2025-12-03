"""Tests for main application."""

import pytest
import tempfile
from pathlib import Path
from src.main import SecretSantaApplication


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_employees_csv(temp_dir):
    """Create sample employees CSV file."""
    csv_file = temp_dir / "employees.csv"
    csv_file.write_text(
        "Employee_Name,Employee_EmailID\n"
        "Alice,alice@example.com\n"
        "Bob,bob@example.com\n"
        "Charlie,charlie@example.com\n"
    )
    return csv_file


@pytest.fixture
def sample_previous_csv(temp_dir):
    """Create sample previous assignments CSV file."""
    csv_file = temp_dir / "previous.csv"
    csv_file.write_text(
        "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
        "Alice,alice@example.com,Bob,bob@example.com\n"
        "Bob,bob@example.com,Charlie,charlie@example.com\n"
        "Charlie,charlie@example.com,Alice,alice@example.com\n"
    )
    return csv_file


class TestSecretSantaApplication:
    """Test main application."""
    
    def test_successful_run(self, temp_dir, sample_employees_csv, sample_previous_csv):
        """Test successful application run."""
        output_file = temp_dir / "output.csv"
        
        app = SecretSantaApplication(
            employees_file=sample_employees_csv,
            previous_file=sample_previous_csv,
            output_file=output_file
        )
        
        success = app.run()
        
        assert success is True
        assert output_file.exists()
    
    def test_run_without_previous_file(self, temp_dir, sample_employees_csv):
        """Test run without previous assignments file."""
        output_file = temp_dir / "output.csv"
        non_existent = temp_dir / "non_existent.csv"
        
        app = SecretSantaApplication(
            employees_file=sample_employees_csv,
            previous_file=non_existent,
            output_file=output_file
        )
        
        success = app.run()
        assert success is True
    
    def test_run_with_missing_employees_file(self, temp_dir):
        """Test run with missing employees file."""
        output_file = temp_dir / "output.csv"
        missing_file = temp_dir / "missing.csv"
        
        app = SecretSantaApplication(
            employees_file=missing_file,
            previous_file=temp_dir / "prev.csv",
            output_file=output_file
        )
        
        success = app.run()
        assert success is False
    
    def test_run_with_invalid_employees(self, temp_dir):
        """Test run with invalid employee data."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,invalid-email\n"
        )
        
        output_file = temp_dir / "output.csv"
        
        app = SecretSantaApplication(
            employees_file=csv_file,
            previous_file=temp_dir / "prev.csv",
            output_file=output_file
        )
        
        success = app.run()
        assert success is False
    
    def test_run_with_insufficient_employees(self, temp_dir):
        """Test run with too few employees."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,alice@example.com\n"
        )
        
        output_file = temp_dir / "output.csv"
        
        app = SecretSantaApplication(
            employees_file=csv_file,
            previous_file=temp_dir / "prev.csv",
            output_file=output_file
        )
        
        success = app.run()
        assert success is False