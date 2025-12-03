"""Tests for validation module."""

import pytest
from src.models import Employee
from src.validator import Validator
from src.exceptions import ValidationError


class TestEmailValidation:
    """Test cases for email validation."""
    
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "test.user@example.com",
        "user+tag@example.co.uk",
        "user123@test-domain.com",
    ])
    def test_valid_email_formats(self, email):
        """Test various valid email formats."""
        assert Validator.validate_email(email) is True
    
    @pytest.mark.parametrize("email", [
        "invalid",
        "@example.com",
        "user@",
        "user @example.com",
        "user@example",
        "",
    ])
    def test_invalid_email_formats(self, email):
        """Test various invalid email formats."""
        assert Validator.validate_email(email) is False
    
    def test_email_with_spaces(self):
        """Test email validation with spaces."""
        assert Validator.validate_email("  user@example.com  ") is True


class TestEmployeeValidation:
    """Test cases for employee validation."""
    
    def test_validate_valid_employee(self):
        """Test validating a valid employee."""
        emp = Employee(name="John Doe", email="john@example.com")
        Validator.validate_employee(emp)  # Should not raise
    
    def test_validate_employee_invalid_email(self):
        """Test validating employee with invalid email."""
        emp = Employee(name="John Doe", email="invalid-email")
        with pytest.raises(ValidationError, match="Invalid email format"):
            Validator.validate_employee(emp)
    
    def test_validate_employee_with_whitespace_name(self):
        """Test validating employee with only whitespace name."""
        with pytest.raises(ValueError):
            Employee(name="   ", email="john@example.com")


class TestEmployeeListValidation:
    """Test cases for employee list validation."""
    
    def test_validate_valid_employee_list(self):
        """Test validating a valid list of employees."""
        employees = [
            Employee(name="John Doe", email="john@example.com"),
            Employee(name="Jane Smith", email="jane@example.com"),
            Employee(name="Bob Johnson", email="bob@example.com"),
        ]
        Validator.validate_employees(employees)  # Should not raise
    
    def test_validate_empty_list(self):
        """Test that empty list raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            Validator.validate_employees([])
    
    def test_validate_insufficient_employees(self):
        """Test that too few employees raises error."""
        employees = [Employee(name="John Doe", email="john@example.com")]
        with pytest.raises(ValidationError, match="At least 2 employees required"):
            Validator.validate_employees(employees, min_count=2)
    
    def test_validate_duplicate_email(self):
        """Test that duplicate emails are detected."""
        employees = [
            Employee(name="John Doe", email="john@example.com"),
            Employee(name="Jane Smith", email="JOHN@example.com"),  # Same email
        ]
        with pytest.raises(ValidationError, match="Duplicate email"):
            Validator.validate_employees(employees)
    
    def test_validate_duplicate_name(self):
        """Test that duplicate names are detected."""
        employees = [
            Employee(name="John Doe", email="john1@example.com"),
            Employee(name="john doe", email="john2@example.com"),  # Same name
        ]
        with pytest.raises(ValidationError, match="Duplicate name"):
            Validator.validate_employees(employees)
    
    def test_validate_invalid_employee_in_list(self):
        """Test that invalid employee in list is caught."""
        employees = [
            Employee(name="John Doe", email="john@example.com"),
            Employee(name="Jane Smith", email="invalid-email"),
        ]
        with pytest.raises(ValidationError, match="Invalid email format"):
            Validator.validate_employees(employees)


class TestCSVHeaderValidation:
    """Test cases for CSV header validation."""
    
    def test_validate_valid_headers(self):
        """Test validating correct headers."""
        headers = ['Employee_Name', 'Employee_EmailID']
        required = ['Employee_Name', 'Employee_EmailID']
        Validator.validate_csv_headers(headers, required)  # Should not raise
    
    def test_validate_missing_headers(self):
        """Test that missing headers are detected."""
        headers = ['Employee_Name']
        required = ['Employee_Name', 'Employee_EmailID']
        with pytest.raises(ValidationError, match="Missing required CSV fields"):
            Validator.validate_csv_headers(headers, required)
    
    def test_validate_extra_headers_allowed(self):
        """Test that extra headers are allowed."""
        headers = ['Employee_Name', 'Employee_EmailID', 'Department']
        required = ['Employee_Name', 'Employee_EmailID']
        Validator.validate_csv_headers(headers, required)  # Should not raise
    
    def test_validate_headers_with_whitespace(self):
        """Test validating headers with whitespace."""
        headers = ['  Employee_Name  ', '  Employee_EmailID  ']
        required = ['Employee_Name', 'Employee_EmailID']
        Validator.validate_csv_headers(headers, required)  # Should not raise
    
    def test_validate_multiple_missing_headers(self):
        """Test error message includes all missing headers."""
        headers = ['Department']
        required = ['Employee_Name', 'Employee_EmailID']
        with pytest.raises(ValidationError, match="Employee_Name"):
            Validator.validate_csv_headers(headers, required)