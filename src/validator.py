import re
from typing import List, Set
from .models import Employee
from .exceptions import ValidationError


class Validator:
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        return bool(Validator.EMAIL_REGEX.match(email.strip()))
    
    @staticmethod
    def validate_employee(employee: Employee) -> None:
        if not employee.name.strip():
            raise ValidationError("Employee name cannot be empty")
        
        if not Validator.validate_email(employee.email):
            raise ValidationError(
                f"Invalid email format for {employee.name}: {employee.email}"
            )
    
    @staticmethod
    def validate_employees(employees: List[Employee], min_count: int = 2) -> None:
        if not employees:
            raise ValidationError("Employee list cannot be empty")
        
        if len(employees) < min_count:
            raise ValidationError(
                f"At least {min_count} employees required, got {len(employees)}"
            )
        
        # Validate each employee
        for employee in employees:
            Validator.validate_employee(employee)
        
        # Check for duplicates
        Validator._check_duplicates(employees)
    
    @staticmethod
    def _check_duplicates(employees: List[Employee]) -> None:
        seen_emails: Set[str] = set()
        
        for employee in employees:
            email_lower = employee.email.lower()
            
            if email_lower in seen_emails:
                raise ValidationError(
                    f"Duplicate email found: {employee.email}"
                )
            
            seen_emails.add(email_lower)
    
    @staticmethod
    def validate_csv_headers(headers: List[str], required_fields: List[str]) -> None:
        headers_set = set(h.strip() for h in headers)
        required_set = set(required_fields)
        
        missing = required_set - headers_set
        if missing:
            raise ValidationError(
                f"Missing required CSV fields: {', '.join(missing)}"
            )