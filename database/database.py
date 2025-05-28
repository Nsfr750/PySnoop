"""
Card database implementation for Stripe Snoop.
"""

from typing import List, Dict, Type, Optional, Any
import importlib
import os
import json
from pathlib import Path

from .test_result import TestResult
from .card_tests import GenericTest, CARD_TESTS

class CardDatabase:
    """
    Manages all card tests and runs them against swiped cards.
    """
    
    def __init__(self, test_classes: Optional[List[Type[GenericTest]]] = None):
        """
        Initialize the card database with the specified test classes.
        
        Args:
            test_classes: Optional list of test classes to use. If None, uses all available tests.
        """
        self.tests: List[GenericTest] = []
        
        # Initialize with default tests if none provided
        if test_classes is None:
            test_classes = list(CARD_TESTS.values())
        
        for test_class in test_classes:
            self.add_test(test_class())
    
    def add_test(self, test: GenericTest) -> None:
        """
        Add a test to the database.
        
        Args:
            test: The test to add
        """
        if test not in self.tests:
            self.tests.append(test)
    
    def run_tests(self, card) -> TestResult:
        """
        Run all tests against the given card.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The first valid test result, or an invalid result if no tests matched
        """
        for test in self.tests:
            if test.meets_requirements(card):
                result = test.run_test(card)
                if result.is_valid():
                    return result
        
        # No tests matched
        return TestResult()
    
    def get_available_tests(self) -> List[Dict[str, Any]]:
        """
        Get information about all available tests.
        
        Returns:
            List of dictionaries containing test information
        """
        return [{
            'name': test.__class__.__name__,
            'required_tracks': test.required_tracks
        } for test in self.tests]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the database to a dictionary.
        
        Returns:
            Dictionary representation of the database
        """
        return {
            'tests': [test.to_dict() for test in self.tests]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CardDatabase':
        """
        Create a CardDatabase from a dictionary.
        
        Args:
            data: Dictionary containing database data
            
        Returns:
            A new CardDatabase instance
        """
        db = cls()
        db.tests = []
        
        for test_data in data.get('tests', []):
            test_type = test_data.get('type')
            if test_type in CARD_TESTS:
                test_class = CARD_TESTS[test_type.lower()]
                test = test_class()
                test.required_tracks = test_data.get('required_tracks', [])
                db.add_test(test)
        
        return db
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save the database to a JSON file.
        
        Args:
            filename: Path to the output file
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filename: str) -> Optional['CardDatabase']:
        """
        Load a database from a JSON file.
        
        Args:
            filename: Path to the input file
            
        Returns:
            A new CardDatabase instance, or None if loading failed
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading database: {e}")
            return None
    
    @classmethod
    def load_default_tests(cls) -> 'CardDatabase':
        """
        Load the default set of card tests.
        
        Returns:
            A new CardDatabase with default tests
        """
        return cls()
    
    @classmethod
    def load_from_directory(cls, directory: str) -> 'CardDatabase':
        """
        Load card tests from a directory of Python modules.
        
        Args:
            directory: Path to the directory containing test modules
            
        Returns:
            A new CardDatabase with tests from the directory
        """
        db = cls()
        
        # Add the directory to the Python path
        import sys
        if directory not in sys.path:
            sys.path.insert(0, directory)
        
        # Find all Python files in the directory
        for filename in Path(directory).glob('*.py'):
            if filename.stem == '__init__':
                continue
                
            module_name = filename.stem
            try:
                module = importlib.import_module(module_name)
                
                # Find all test classes in the module
                for name, obj in module.__dict__.items():
                    if (isinstance(obj, type) and 
                            issubclass(obj, GenericTest) and 
                            obj != GenericTest):
                        db.add_test(obj())
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")
        
        return db
