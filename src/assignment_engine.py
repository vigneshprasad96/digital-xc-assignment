import random
import logging
from typing import List, Dict, Set, Optional
from abc import ABC, abstractmethod
from .models import Employee, Assignment
from .exceptions import (
    AssignmentError,
    InsufficientEmployeesError,
    NoValidAssignmentError
)
from .config import Config


logger = logging.getLogger(__name__)


class AssignmentStrategy(ABC):
    
    @abstractmethod
    def generate(
        self,
        employees: List[Employee],
        previous_assignments: Dict[Employee, Employee]
    ) -> List[Assignment]:
        pass


class RandomDerangementStrategy(AssignmentStrategy):
    def __init__(self, config: Optional[Config] = None):
        
        self.config = config or Config()
        self.max_attempts = self.config.max_assignment_attempts
    
    def generate(
        self,
        employees: List[Employee],
        previous_assignments: Dict[Employee, Employee]
    ) -> List[Assignment]:
        if len(employees) < self.config.min_employees:
            raise InsufficientEmployeesError(
                f"Need at least {self.config.min_employees} employees"
            )
        
        logger.info(
            f"Generating assignments for {len(employees)} employees "
            f"with {len(previous_assignments)} previous assignments to avoid"
        )
        
        for attempt in range(self.max_attempts):
            try:
                assignments = self._attempt_assignment(
                    employees, 
                    previous_assignments
                )
                logger.info(f"Found valid assignment on attempt {attempt + 1}")
                return assignments
            except AssignmentError:
                continue
        
        raise NoValidAssignmentError(
            f"Could not find valid assignment after {self.max_attempts} attempts"
        )
    
    def _attempt_assignment(
        self,
        employees: List[Employee],
        previous_assignments: Dict[Employee, Employee]
    ) -> List[Assignment]:
        # Create shuffled list of potential secret children
        available = employees.copy()
        random.shuffle(available)
        
        assignments = []
        used_children: Set[Employee] = set()
        
        for giver in employees:
            # Find valid secret child
            child = self._find_valid_child(
                giver,
                available,
                used_children,
                previous_assignments.get(giver)
            )
            
            if child is None:
                raise AssignmentError("No valid child found")
            
            assignments.append(Assignment(employee=giver, secret_child=child))
            used_children.add(child)
        
        return assignments
    
    def _find_valid_child(
        self,
        giver: Employee,
        available: List[Employee],
        used: Set[Employee],
        previous_child: Optional[Employee]
    ) -> Optional[Employee]:
        for child in available:
            # Check all constraints:
            # 1. Not already used
            # 2. Not the giver themselves (no self-assignment)
            # 3. Not the same as previous year (NO OVERLAP)
            if (child not in used and 
                child != giver and 
                child != previous_child):
                return child
        return None


class AssignmentEngine:
    def __init__(
        self,
        strategy: Optional[AssignmentStrategy] = None,
        config: Optional[Config] = None
    ):
        self.config = config or Config()
        self.strategy = strategy or RandomDerangementStrategy(self.config)
    
    def create_assignments(
        self,
        employees: List[Employee],
        previous_assignments: List[Assignment]
    ) -> List[Assignment]:
        # Convert previous assignments to lookup dict
        # This maps each employee to their secret child from last year
        previous_map = {
            assignment.employee: assignment.secret_child
            for assignment in previous_assignments
        }
        
        logger.info(f"Previous assignments map: {len(previous_map)} entries")
        for emp, child in previous_map.items():
            logger.debug(f"  {emp.name} gave to {child.name} last year (will avoid)")
        
        # Generate new assignments using strategy
        return self.strategy.generate(employees, previous_map)