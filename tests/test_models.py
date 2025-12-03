import pytest
from src.models import Employee, Assignment


class TestEmployee:
    """Test cases for Employee model."""
    
    def test_create_valid_employee(self):
        """Test creating a valid employee."""
        emp = Employee(name="John Doe", email="john@example.com")
        assert emp.name == "John Doe"
        assert emp.email == "john@example.com"
    
    def test_employee_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Employee(name="", email="john@example.com")
    
    def test_employee_equality(self):
        """Test employee equality (case-insensitive)."""
        emp1 = Employee(name="John Doe", email="john@example.com")
        emp2 = Employee(name="john doe", email="JOHN@EXAMPLE.COM")
        assert emp1 == emp2
    
    def test_employee_hashable(self):
        """Test that employees can be used in sets and dicts."""
        emp1 = Employee(name="John Doe", email="john@example.com")
        emp2 = Employee(name="Jane Doe", email="jane@example.com")
        employee_set = {emp1, emp2}
        assert len(employee_set) == 2


class TestAssignment:
    """Test cases for Assignment model."""
    
    def test_create_valid_assignment(self):
        """Test creating a valid assignment."""
        giver = Employee(name="John Doe", email="john@example.com")
        receiver = Employee(name="Jane Doe", email="jane@example.com")
        assignment = Assignment(employee=giver, secret_child=receiver)
        assert assignment.employee == giver
        assert assignment.secret_child == receiver
    
    def test_self_assignment_raises_error(self):
        """Test that self-assignment raises ValueError."""
        emp = Employee(name="John Doe", email="john@example.com")
        with pytest.raises(ValueError, match="cannot be assigned to themselves"):
            Assignment(employee=emp, secret_child=emp)
    
    def test_assignment_to_dict(self):
        """Test converting assignment to dictionary."""
        giver = Employee(name="John Doe", email="john@example.com")
        receiver = Employee(name="Jane Doe", email="jane@example.com")
        assignment = Assignment(employee=giver, secret_child=receiver)
        
        result = assignment.to_dict()
        assert result['Employee_Name'] == "John Doe"
        assert result['Secret_Child_Name'] == "Jane Doe"