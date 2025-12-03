import csv
import logging
from pathlib import Path
from typing import List, Optional

from .models import Employee, Assignment
from .exceptions import FileOperationError, ValidationError
from .validator import Validator
from .config import Config


logger = logging.getLogger(__name__)


class CSVHandler:
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
    
    def read_employees(self, file_path: Path) -> List[Employee]:
        logger.info(f"Reading employees from {file_path}")
        
        if not file_path.exists():
            raise FileOperationError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate headers
                if reader.fieldnames:
                    Validator.validate_csv_headers(
                        reader.fieldnames, 
                        self.config.employee_fields
                    )
                
                employees = []
                for row_num, row in enumerate(reader, start=2):
                    try:
                        employee = Employee(
                            name=row['Employee_Name'].strip(),
                            email=row['Employee_EmailID'].strip()
                        )
                        Validator.validate_employee(employee)
                        employees.append(employee)
                    except (KeyError, ValueError) as e:
                        raise ValidationError(
                            f"Error in row {row_num}: {str(e)}"
                        )
                
                logger.info(f"Successfully read {len(employees)} employees")
                return employees
                
        except csv.Error as e:
            raise FileOperationError(f"CSV parsing error: {str(e)}")
        except IOError as e:
            raise FileOperationError(f"File I/O error: {str(e)}")
    
    def read_previous_assignments(
        self, 
        file_path: Path
    ) -> List[Assignment]:
        logger.info(f"Reading previous assignments from {file_path}")
        
        if not file_path.exists():
            logger.warning(f"Previous assignments file not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate headers
                if reader.fieldnames:
                    Validator.validate_csv_headers(
                        reader.fieldnames,
                        self.config.assignment_fields
                    )
                
                assignments = []
                for row in reader:
                    try:
                        assignment = Assignment.from_dict(row)
                        assignments.append(assignment)
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Skipping invalid assignment: {str(e)}")
                        continue
                
                logger.info(
                    f"Successfully read {len(assignments)} previous assignments"
                )
                return assignments
                
        except csv.Error as e:
            raise FileOperationError(f"CSV parsing error: {str(e)}")
        except IOError as e:
            raise FileOperationError(f"File I/O error: {str(e)}")
    
    def write_assignments(
        self, 
        assignments: List[Assignment], 
        file_path: Path
    ) -> None:
        logger.info(f"Writing {len(assignments)} assignments to {file_path}")
        
        # Ensure output directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=self.config.assignment_fields
                )
                writer.writeheader()
                
                for assignment in assignments:
                    writer.writerow(assignment.to_dict())
            
            logger.info(f"Successfully wrote assignments to {file_path}")
            
        except IOError as e:
            raise FileOperationError(f"Failed to write file: {str(e)}")