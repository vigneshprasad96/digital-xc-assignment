# Secret Santa Assignment System

Automated Secret Santa gift exchange assignment system for Acme company employees.

## Overview

This system automatically assigns Secret Santa gift exchange pairs while ensuring:
- No one is assigned to themselves
- No duplicate assignments from the previous year
- Each employee gives and receives exactly once
- All email addresses are unique

## Requirements

- Python 3.12+
- Poetry (for dependency management)

## Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd digital-xc-assignment

# Install dependencies
poetry install
```

## Quick Start

1. **Run the application**:
```bash
poetry run secret-santa
```

2. **Check the output** in `data/output/secret_santa_assignments.csv`

## Usage

### Basic Usage (with default file paths)
```bash
poetry run secret-santa
```

### Custom File Paths
```bash
poetry run secret-santa \
  --employees path/to/employees.csv \
  --previous path/to/previous_assignments.csv \
  --output path/to/output.csv
```

### Using Python Module
```bash
python -m src.main
```

## Input File Format

### Required: Employee List
File must contain exactly these headers:
- `Employee_Name`: Full name of employee
- `Employee_EmailID`: Email address (must be unique)

**Minimum 2 employees required**

### Optional: Previous Assignments
File must contain exactly these headers:
- `Employee_Name`: Employee giving the gift
- `Employee_EmailID`: Email of the giver
- `Secret_Child_Name`: Employee receiving the gift
- `Secret_Child_EmailID`: Email of the receiver

## Output Format

The system generates a CSV file with assignments:
```csv
Employee_Name,Employee_EmailID,Secret_Child_Name,Secret_Child_EmailID
Alice Johnson,alice@acme.com,Diana Prince,diana@acme.com
Bob Smith,bob@acme.com,Alice Johnson,alice@acme.com
Charlie Brown,charlie@acme.com,Bob Smith,bob@acme.com
Diana Prince,diana@acme.com,Charlie Brown,charlie@acme.com
```

## Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## Project Structure
```
digital-xc-assignment/
├── src/
│   ├── models.py              # Employee and Assignment data models
│   ├── config.py              # Configuration (Singleton pattern)
│   ├── validator.py           # Input validation
│   ├── csv_handler.py         # CSV file operations
│   ├── assignment_engine.py   # Assignment generation logic
│   ├── main.py                # Application entry point
│   └── exceptions.py          # Custom exception classes
├── tests/                     # Test suite
├── data/
│   ├── employees.csv          # Input: employee list
│   ├── previous_assignments.csv  # Input: last year (optional)
│   └── output/                # Output directory
├── pyproject.toml             # Project configuration
└── README.md
```


## Error Handling

The system handles various errors gracefully:
- Missing or invalid CSV files
- Incorrect file formats
- Invalid email addresses
- Duplicate email addresses
- Insufficient number of employees
- Impossible assignment constraints

Detailed logs are written to `secret_santa.log`

## License

MIT License

## Author

Vignesh Prasad

## Support

For issues or questions, please check `secret_santa.log` for detailed error messages.