"""Tests for configuration singleton."""

import pytest
from pathlib import Path
from src.config import Config


class TestConfigSingleton:
    """Test singleton pattern implementation."""
    
    def setup_method(self):
        """Reset singleton before each test."""
        Config.reset()
    
    def test_singleton_same_instance(self):
        """Test that Config returns same instance."""
        config1 = Config()
        config2 = Config()
        assert config1 is config2
    
    def test_singleton_initialized_once(self):
        """Test that Config is initialized only once."""
        config1 = Config()
        original_attempts = config1.max_assignment_attempts
        
        # Modify value
        config1.max_assignment_attempts = 5000
        
        # Create new reference
        config2 = Config()
        
        # Should have modified value
        assert config2.max_assignment_attempts == 5000
        assert config1 is config2
    
    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.data_dir == Path('data')
        assert config.min_employees == 2
        assert config.max_assignment_attempts == 1000
        assert len(config.employee_fields) == 2
        assert len(config.assignment_fields) == 4
    
    def test_ensure_output_directory(self, tmp_path):
        """Test output directory creation."""
        config = Config()
        config.output_dir = tmp_path / "test_output"
        
        config.ensure_output_directory()
        
        assert config.output_dir.exists()
    
    def test_reset_singleton(self):
        """Test resetting singleton instance."""
        config1 = Config()
        config1.max_assignment_attempts = 5000
        
        Config.reset()
        
        config2 = Config()
        assert config2.max_assignment_attempts == 1000  # Back to default
        assert config1 is not config2