from dataclasses import dataclass


@dataclass(frozen=True)
class Employee:
    """Immutable employee data model."""
    
    name: str
    email: str
    
    def __post_init__(self):
        """Validate employee data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Employee name cannot be empty")
        if not self.email or not self.email.strip():
            raise ValueError("Employee email cannot be empty")
    
    def __hash__(self):
        """Make Employee hashable for use in sets and dicts."""
        return hash((self.name.lower(), self.email.lower()))
    
    def __eq__(self, other):
        """Compare employees case-insensitively."""
        if not isinstance(other, Employee):
            return False
        return (self.name.lower() == other.name.lower() and 
                self.email.lower() == other.email.lower())


@dataclass
class Assignment:
    """Represents a Secret Santa assignment."""
    
    employee: Employee
    secret_child: Employee
    
    def __post_init__(self):
        """Validate assignment after initialization."""
        if self.employee == self.secret_child:
            raise ValueError("Employee cannot be assigned to themselves")
    
    def to_dict(self) -> dict:
        """Convert assignment to dictionary format."""
        return {
            'Employee_Name': self.employee.name,
            'Employee_EmailID': self.employee.email,
            'Secret_Child_Name': self.secret_child.name,
            'Secret_Child_EmailID': self.secret_child.email
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Assignment':
        """Create assignment from dictionary."""
        employee = Employee(
            name=data['Employee_Name'],
            email=data['Employee_EmailID']
        )
        secret_child = Employee(
            name=data['Secret_Child_Name'],
            email=data['Secret_Child_EmailID']
        )
        return cls(employee=employee, secret_child=secret_child)