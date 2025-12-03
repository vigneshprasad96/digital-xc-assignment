"""Tests for assignment engine - focuses on NO OVERLAP constraint."""

import pytest
from src.models import Employee, Assignment
from src.assignment_engine import AssignmentEngine, RandomDerangementStrategy
from src.exceptions import InsufficientEmployeesError


@pytest.fixture
def employees():
    """Create a list of test employees."""
    return [
        Employee(name="Alice", email="alice@example.com"),
        Employee(name="Bob", email="bob@example.com"),
        Employee(name="Charlie", email="charlie@example.com"),
        Employee(name="Diana", email="diana@example.com"),
        Employee(name="Eve", email="eve@example.com"),
    ]


@pytest.fixture
def previous_assignments(employees):
    """Create previous year's assignments."""
    return [
        Assignment(employee=employees[0], secret_child=employees[1]),  # Alice -> Bob
        Assignment(employee=employees[1], secret_child=employees[2]),  # Bob -> Charlie
        Assignment(employee=employees[2], secret_child=employees[3]),  # Charlie -> Diana
        Assignment(employee=employees[3], secret_child=employees[4]),  # Diana -> Eve
        Assignment(employee=employees[4], secret_child=employees[0]),  # Eve -> Alice
    ]


class TestNoOverlapConstraint:
    """Test that previous assignments are NEVER repeated."""
    
    def test_no_repeats_from_previous_year(self, employees, previous_assignments):
        """CRITICAL: Test that previous assignments are not repeated."""
        strategy = RandomDerangementStrategy()
        previous_map = {a.employee: a.secret_child for a in previous_assignments}
        
        # Run multiple times to ensure consistency
        for iteration in range(20):
            new_assignments = strategy.generate(employees, previous_map)
            
            # Check that NO assignment matches previous year
            for assignment in new_assignments:
                previous_child = previous_map.get(assignment.employee)
                if previous_child:
                    assert assignment.secret_child != previous_child, \
                        f"OVERLAP DETECTED: {assignment.employee.name} got same child " \
                        f"({assignment.secret_child.name}) as last year!"
    
    def test_no_self_assignments(self, employees):
        """Test that no one is assigned to themselves."""
        strategy = RandomDerangementStrategy()
        assignments = strategy.generate(employees, {})
        
        for assignment in assignments:
            assert assignment.employee != assignment.secret_child
    
    def test_all_employees_assigned(self, employees):
        """Test that each employee appears exactly once as giver and receiver."""
        strategy = RandomDerangementStrategy()
        assignments = strategy.generate(employees, {})
        
        givers = {a.employee for a in assignments}
        receivers = {a.secret_child for a in assignments}
        
        assert givers == set(employees)
        assert receivers == set(employees)
    
    def test_insufficient_employees(self):
        """Test error with too few employees."""
        strategy = RandomDerangementStrategy()
        employees = [Employee(name="Alice", email="alice@example.com")]
        
        with pytest.raises(InsufficientEmployeesError):
            strategy.generate(employees, {})