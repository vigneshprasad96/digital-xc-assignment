import logging
from pathlib import Path
from typing import Optional


class Config:
    _instance: Optional['Config'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not Config._initialized:
            self._setup_defaults()
            Config._initialized = True
    
    def _setup_defaults(self):
        # File paths
        self.data_dir = Path('data')
        self.output_dir = self.data_dir / 'output'
        self.employees_file = self.data_dir / 'Employee-List.csv'
        self.previous_assignments_file = self.data_dir / 'secret_santa_assignments_old.csv'
        self.output_file = self.output_dir / 'secret_santa_assignments.csv'
        
        # CSV field names
        self.employee_fields = ['Employee_Name', 'Employee_EmailID']
        self.assignment_fields = [
            'Employee_Name', 
            'Employee_EmailID',
            'Secret_Child_Name',
            'Secret_Child_EmailID'
        ]
        
        # Assignment constraints
        self.max_assignment_attempts = 1000
        self.min_employees = 2
        
        # Logging
        self.log_level = logging.INFO
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    def setup_logging(self):
        logging.basicConfig(
            level=self.log_level,
            format=self.log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('secret_santa.log')
            ]
        )
    
    def ensure_output_directory(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def reset(cls):
        cls._instance = None
        cls._initialized = False