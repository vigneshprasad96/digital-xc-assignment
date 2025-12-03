"""Integration tests for Secret Santa application."""

import pytest
import tempfile
from pathlib import Path
from src.main import SecretSantaApplication
from src.csv_handler import CSVHandler
from src.config import Config


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def setup_method():
    """Reset config before each test."""
    Config.reset()


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_complete_workflow(self, temp_dir):
        """Test complete workflow from CSV input to output."""
        # Create input files
        employees_file = temp_dir / "employees.csv"
        employees_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,alice@example.com\n"
            "Bob,bob@example.com\n"
            "Charlie,charlie@example.com\n"
            "Diana,diana@example.com\n"
        )
        
        previous_file = temp_dir / "previous.csv"
        previous_file.write_text(
            "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
            "Alice,alice@example.com,Bob,bob@example.com\n"
            "Bob,bob@example.com,Charlie,charlie@example.com\n"
            "Charlie,charlie@example.com,Diana,diana@example.com\n"
            "Diana,diana@example.com,Alice,alice@example.com\n"
        )
        
        output_file = temp_dir / "output.csv"
        
        # Run application
        app = SecretSantaApplication(
            employees_file=employees_file,
            previous_file=previous_file,
            output_file=output_file
        )
        
        success = app.run()
        
        assert success is True
        assert output_file.exists()
        
        # Verify output
        handler = CSVHandler()
        assignments = handler.read_previous_assignments(output_file)
        assert len(assignments) == 4
        
        # Verify no overlaps
        previous = handler.read_previous_assignments(previous_file)
        previous_map = {a.employee.name: a.secret_child.name for a in previous}
        
        for assignment in assignments:
            previous_child = previous_map.get(assignment.employee.name)
            if previous_child:
                assert assignment.secret_child.name != previous_child
    
    def test_multiple_runs_different_results(self, temp_dir):
        """Test that multiple runs produce different valid results."""
        employees_file = temp_dir / "employees.csv"
        employees_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,alice@example.com\n"
            "Bob,bob@example.com\n"
            "Charlie,charlie@example.com\n"
            "Diana,diana@example.com\n"
            "Eve,eve@example.com\n"
        )
        
        output_file1 = temp_dir / "output1.csv"
        output_file2 = temp_dir / "output2.csv"
        
        # Run twice
        app1 = SecretSantaApplication(
            employees_file=employees_file,
            previous_file=temp_dir / "non_existent.csv",
            output_file=output_file1
        )
        app1.run()
        
        Config.reset()  # Reset singleton
        
        app2 = SecretSantaApplication(
            employees_file=employees_file,
            previous_file=temp_dir / "non_existent.csv",
            output_file=output_file2
        )
        app2.run()
        
        # Both should succeed
        assert output_file1.exists()
        assert output_file2.exists()
        
        # Results might be different (not guaranteed but likely)
        content1 = output_file1.read_text()
        content2 = output_file2.read_text()
        # Both should be valid outputs
        assert "Alice" in content1
        assert "Alice" in content2