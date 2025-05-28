"""
TestResult class for storing and managing card test results.
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field

@dataclass
class TestResult:
    """
    Stores the results of a card test, including any information found in the card database.
    """
    
    card_type: str = ""
    notes: str = ""
    unknowns: str = ""
    valid: bool = False
    tags: List[Tuple[str, str]] = field(default_factory=list)  # (name, value) pairs
    extra_tags: List[str] = field(default_factory=list)
    
    def set_card_type(self, card_type: str) -> None:
        """Set the card type."""
        self.card_type = card_type
        self.valid = bool(card_type)
    
    def set_notes(self, notes: str) -> None:
        """Set the notes for this result."""
        self.notes = notes
    
    def set_unknowns(self, unknowns: str) -> None:
        """Set any unknown fields found."""
        self.unknowns = unknowns
    
    def add_tag(self, name: str, value: str) -> None:
        """
        Add a name-value tag to the result.
        
        Args:
            name: The name of the tag
            value: The value of the tag
        """
        # Check if tag already exists
        for i, (tag_name, _) in enumerate(self.tags):
            if tag_name == name:
                # Update existing tag
                self.tags[i] = (name, value)
                return
        
        # Add new tag
        self.tags.append((name, value))
    
    def add_extra_tag(self, tag: str) -> None:
        """
        Add an extra tag to the result.
        
        Args:
            tag: The tag to add
        """
        if tag and tag not in self.extra_tags:
            self.extra_tags.append(tag)
    
    def get_name_tag(self, index: int) -> str:
        """
        Get the name of a tag by index.
        
        Args:
            index: The index of the tag
            
        Returns:
            The tag name, or empty string if index is out of range
        """
        if 0 <= index < len(self.tags):
            return self.tags[index][0]
        return ""
    
    def get_data_tag(self, index: int) -> str:
        """
        Get the value of a tag by index.
        
        Args:
            index: The index of the tag
            
        Returns:
            The tag value, or empty string if index is out of range
        """
        if 0 <= index < len(self.tags):
            return self.tags[index][1]
        return ""
    
    def get_extra_tag(self, index: int) -> str:
        """
        Get an extra tag by index.
        
        Args:
            index: The index of the extra tag
            
        Returns:
            The extra tag, or empty string if index is out of range
        """
        if 0 <= index < len(self.extra_tags):
            return self.extra_tags[index]
        return ""
    
    def get_card_type(self) -> str:
        """Get the card type."""
        return self.card_type
    
    def get_notes(self) -> str:
        """Get the notes."""
        return self.notes
    
    def get_unknowns(self) -> str:
        """Get any unknown fields."""
        return self.unknowns
    
    def get_num_tags(self) -> int:
        """Get the number of name-value tags."""
        return len(self.tags)
    
    def get_num_extra_tags(self) -> int:
        """Get the number of extra tags."""
        return len(self.extra_tags)
    
    def is_valid(self) -> bool:
        """Check if the test result is valid."""
        return self.valid
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the test result to a dictionary.
        
        Returns:
            A dictionary representation of the test result
        """
        return {
            'card_type': self.card_type,
            'notes': self.notes,
            'unknowns': self.unknowns,
            'valid': self.valid,
            'tags': [{'name': name, 'value': value} for name, value in self.tags],
            'extra_tags': self.extra_tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """
        Create a TestResult from a dictionary.
        
        Args:
            data: Dictionary containing test result data
            
        Returns:
            A new TestResult instance
        """
        result = cls()
        result.card_type = data.get('card_type', '')
        result.notes = data.get('notes', '')
        result.unknowns = data.get('unknowns', '')
        result.valid = data.get('valid', False)
        result.tags = [(tag['name'], tag['value']) for tag in data.get('tags', [])]
        result.extra_tags = data.get('extra_tags', [])
        return result
