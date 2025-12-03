import sys
import logging
from pathlib import Path
from typing import Optional

from .config import Config
from .csv_handler import CSVHandler
from .assignment_engine import AssignmentEngine, RandomDerangementStrategy
from .validator import Validator
from .exceptions import SecretSantaException


logger = logging.getLogger(__name__)


class SecretSantaApplication:
    
    def __init__(
        self,
        employees_file: Optional[Path] = None,
        previous_file: Optional[Path] = None,
        output_file: Optional[Path] = None
    ):
        
        self.config = Config()
        self.config.setup_logging()
        self.config.ensure_output_directory()
        
        # Override paths if provided
        self.employees_file = employees_file or self.config.employees_file
        self.previous_file = previous_file or self.config.previous_assignments_file
        self.output_file = output_file or self.config.output_file
        
        # Initialize components
        self.csv_handler = CSVHandler(self.config)
        self.assignment_engine = AssignmentEngine(
            strategy=RandomDerangementStrategy(self.config),
            config=self.config
        )
    
    def run(self) -> bool:
        try:
            logger.info("=" * 60)
            logger.info("Secret Santa Assignment System Started")
            logger.info("=" * 60)
            
            # Step 1: Read employees
            logger.info("Step 1: Reading employee list...")
            employees = self.csv_handler.read_employees(self.employees_file)
            
            # Step 2: Validate employees
            logger.info("Step 2: Validating employee data...")
            Validator.validate_employees(employees, self.config.min_employees)
            logger.info(f"✓ Validated {len(employees)} employees")
            
            # Step 3: Read previous assignments
            logger.info("Step 3: Reading previous assignments...")
            previous_assignments = self.csv_handler.read_previous_assignments(
                self.previous_file
            )
            logger.info(f"✓ Found {len(previous_assignments)} previous assignments")
            
            # Step 4: Generate new assignments (NO OVERLAPS with previous)
            logger.info("Step 4: Generating Secret Santa assignments...")
            logger.info("  -> Ensuring NO overlaps with previous year assignments")
            new_assignments = self.assignment_engine.create_assignments(
                employees,
                previous_assignments
            )
            logger.info(f"✓ Generated {len(new_assignments)} new assignments")
            
            # Step 5: Write output
            logger.info("Step 5: Writing assignments to file...")
            self.csv_handler.write_assignments(new_assignments, self.output_file)
            logger.info(f"✓ Output written to: {self.output_file}")
            
            # Summary
            logger.info("=" * 60)
            logger.info("SUCCESS! Secret Santa assignments completed")
            logger.info(f"Output file: {self.output_file.absolute()}")
            logger.info("=" * 60)
            
            return True
            
        except SecretSantaException as e:
            logger.error(f"Application error: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Secret Santa Assignment System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default file paths from config
  python -m src.main
  
  # Specify custom file paths
  python -m src.main --employees data/employees.csv --output data/output/assignments.csv
  
  # Specify previous assignments to avoid overlaps
  python -m src.main --previous data/previous_assignments.csv
        """
    )
    
    parser.add_argument(
        '--employees',
        type=Path,
        help='Path to employees CSV file'
    )
    parser.add_argument(
        '--previous',
        type=Path,
        help='Path to previous assignments CSV file (to avoid overlaps)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Path for output CSV file'
    )
    
    args = parser.parse_args()
    
    # Create and run application
    app = SecretSantaApplication(
        employees_file=args.employees,
        previous_file=args.previous,
        output_file=args.output
    )
    
    success = app.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()