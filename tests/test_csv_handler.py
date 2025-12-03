"""Tests for CSV handler."""

import pytest
import tempfile
from pathlib import Path
from src.models import Employee, Assignment
from src.csv_handler import CSVHandler
from src.exceptions import FileOperationError, ValidationError


@pytest.fixture
def csv_handler():
    """Create CSV handler instance."""
    return CSVHandler()


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


class TestReadEmployees:
    """Test cases for reading employees from CSV."""
    
    def test_read_valid_employees(self, csv_handler, temp_dir):
        """Test reading valid employee CSV."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,alice@example.com\n"
            "Bob,bob@example.com\n"
        )
        
        employees = csv_handler.read_employees(csv_file)
        
        assert len(employees) == 2
        assert employees[0].name == "Alice"
        assert employees[1].email == "bob@example.com"
    
    def test_read_nonexistent_file(self, csv_handler, temp_dir):
        """Test reading non-existent file raises error."""
        with pytest.raises(FileOperationError, match="File not found"):
            csv_handler.read_employees(temp_dir / "missing.csv")
    
    def test_read_invalid_headers(self, csv_handler, temp_dir):
        """Test reading CSV with invalid headers."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Name,Email\n"
            "Alice,alice@example.com\n"
        )
        
        with pytest.raises(ValidationError, match="Missing required CSV fields"):
            csv_handler.read_employees(csv_file)
    
    def test_read_invalid_email(self, csv_handler, temp_dir):
        """Test reading CSV with invalid email."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,invalid-email\n"
        )
        
        with pytest.raises(ValidationError, match="Invalid email format"):
            csv_handler.read_employees(csv_file)
    
    def test_read_missing_field(self, csv_handler, temp_dir):
        """Test reading CSV with missing field."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "Alice,\n"
        )
        
        with pytest.raises(ValidationError):
            csv_handler.read_employees(csv_file)
    
    def test_read_csv_with_whitespace(self, csv_handler, temp_dir):
        """Test reading CSV with whitespace."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            "  Alice  ,  alice@example.com  \n"
        )
        
        employees = csv_handler.read_employees(csv_file)
        assert employees[0].name == "Alice"
        assert employees[0].email == "alice@example.com"
    
    def test_read_empty_name(self, csv_handler, temp_dir):
        """Test reading CSV with empty name."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID\n"
            ",alice@example.com\n"
        )
        
        with pytest.raises(ValidationError, match="Error in row 2"):
            csv_handler.read_employees(csv_file)
    
    def test_read_io_error(self, csv_handler, temp_dir):
        """Test handling of I/O errors."""
        csv_file = temp_dir / "employees.csv"
        csv_file.write_text("Employee_Name,Employee_EmailID\n")
        
        # Make file unreadable
        csv_file.chmod(0o000)
        
        try:
            with pytest.raises(FileOperationError, match="File I/O error"):
                csv_handler.read_employees(csv_file)
        finally:
            # Restore permissions for cleanup
            csv_file.chmod(0o644)


class TestReadPreviousAssignments:
    """Test cases for reading previous assignments."""
    
    def test_read_valid_assignments(self, csv_handler, temp_dir):
        """Test reading valid previous assignments."""
        csv_file = temp_dir / "previous.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
            "Alice,alice@example.com,Bob,bob@example.com\n"
            "Bob,bob@example.com,Alice,alice@example.com\n"
        )
        
        assignments = csv_handler.read_previous_assignments(csv_file)
        
        assert len(assignments) == 2
        assert assignments[0].employee.name == "Alice"
        assert assignments[0].secret_child.name == "Bob"
    
    def test_read_nonexistent_previous_file(self, csv_handler, temp_dir):
        """Test reading non-existent previous file returns empty list."""
        assignments = csv_handler.read_previous_assignments(
            temp_dir / "missing.csv"
        )
        assert assignments == []
    
    def test_read_invalid_assignment_skips_row(self, csv_handler, temp_dir):
        """Test that invalid assignments are skipped with warning."""
        csv_file = temp_dir / "previous.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
            "Alice,alice@example.com,Bob,bob@example.com\n"
            ",,,\n"  # Invalid row - empty fields
            "Bob,bob@example.com,Alice,alice@example.com\n"
        )
        
        assignments = csv_handler.read_previous_assignments(csv_file)
        assert len(assignments) == 2  # Invalid row skipped
    
    def test_read_previous_with_invalid_headers(self, csv_handler, temp_dir):
        """Test reading previous assignments with invalid headers."""
        csv_file = temp_dir / "previous.csv"
        csv_file.write_text(
            "Name,Email\n"
            "Alice,alice@example.com\n"
        )
        
        with pytest.raises(ValidationError, match="Missing required CSV fields"):
            csv_handler.read_previous_assignments(csv_file)
    
    def test_read_previous_self_assignment(self, csv_handler, temp_dir):
        """Test reading previous with self-assignment (should skip)."""
        csv_file = temp_dir / "previous.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
            "Alice,alice@example.com,Alice,alice@example.com\n"
            "Bob,bob@example.com,Charlie,charlie@example.com\n"
        )
        
        assignments = csv_handler.read_previous_assignments(csv_file)
        # Self-assignment should be skipped
        assert len(assignments) == 1
        assert assignments[0].employee.name == "Bob"
    
    def test_read_previous_io_error(self, csv_handler, temp_dir):
        """Test handling of I/O errors in previous assignments."""
        csv_file = temp_dir / "previous.csv"
        csv_file.write_text(
            "Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID\n"
        )
        
        # Make file unreadable
        csv_file.chmod(0o000)
        
        try:
            with pytest.raises(FileOperationError, match="File I/O error"):
                csv_handler.read_previous_assignments(csv_file)
        finally:
            # Restore permissions for cleanup
            csv_file.chmod(0o644)


class TestWriteAssignments:
    """Test cases for writing assignments."""
    
    def test_write_valid_assignments(self, csv_handler, temp_dir):
        """Test writing valid assignments."""
        assignments = [
            Assignment(
                employee=Employee("Alice", "alice@example.com"),
                secret_child=Employee("Bob", "bob@example.com")
            ),
            Assignment(
                employee=Employee("Bob", "bob@example.com"),
                secret_child=Employee("Alice", "alice@example.com")
            ),
        ]
        
        output_file = temp_dir / "output.csv"
        csv_handler.write_assignments(assignments, output_file)
        
        # Verify file was created and has correct content
        assert output_file.exists()
        content = output_file.read_text()
        assert "Alice" in content
        assert "Bob" in content
        assert "alice@example.com" in content
    
    def test_write_creates_directory(self, csv_handler, temp_dir):
        """Test that writing creates output directory if needed."""
        output_file = temp_dir / "subdir" / "output.csv"
        assignments = [
            Assignment(
                employee=Employee("Alice", "alice@example.com"),
                secret_child=Employee("Bob", "bob@example.com")
            ),
        ]
        
        csv_handler.write_assignments(assignments, output_file)
        
        assert output_file.exists()
        assert output_file.parent.exists()
    
    def test_write_empty_assignments(self, csv_handler, temp_dir):
        """Test writing empty assignments list."""
        output_file = temp_dir / "output.csv"
        csv_handler.write_assignments([], output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        # Should have headers but no data rows
        assert "Employee_Name" in content
    
    def test_write_io_error(self, csv_handler, temp_dir):
        """Test handling of write I/O errors."""
        output_dir = temp_dir / "readonly"
        output_dir.mkdir()
        output_file = output_dir / "output.csv"
        
        # Make directory read-only
        output_dir.chmod(0o444)
        
        try:
            assignments = [
                Assignment(
                    employee=Employee("Alice", "alice@example.com"),
                    secret_child=Employee("Bob", "bob@example.com")
                ),
            ]
            
            with pytest.raises(FileOperationError, match="Failed to write file"):
                csv_handler.write_assignments(assignments, output_file)
        finally:
            # Restore permissions for cleanup
            output_dir.chmod(0o755)
    
    def test_write_multiple_assignments(self, csv_handler, temp_dir):
        """Test writing multiple assignments."""
        assignments = [
            Assignment(
                employee=Employee("Alice", "alice@example.com"),
                secret_child=Employee("Bob", "bob@example.com")
            ),
            Assignment(
                employee=Employee("Bob", "bob@example.com"),
                secret_child=Employee("Charlie", "charlie@example.com")
            ),
            Assignment(
                employee=Employee("Charlie", "charlie@example.com"),
                secret_child=Employee("Alice", "alice@example.com")
            ),
        ]
        
        output_file = temp_dir / "output.csv"
        csv_handler.write_assignments(assignments, output_file)
        
        # Read back and verify
        content = output_file.read_text()
        lines = content.strip().split('\n')
        assert len(lines) == 4  # 1 header + 3 data rows