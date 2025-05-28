"""
Card test implementations for different card types.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Type, Dict, Any
import re
from card import Card
from .test_result import TestResult

class GenericTest(ABC):
    """
    Abstract base class for all card tests.
    """
    
    def __init__(self):
        """Initialize the test with required tracks."""
        self.required_tracks: List[int] = []
    
    def add_required_track(self, track_num: int) -> None:
        """
        Add a required track for this test.
        
        Args:
            track_num: The track number that is required
        """
        if track_num not in self.required_tracks:
            self.required_tracks.append(track_num)
    
    def meets_requirements(self, card) -> bool:
        """
        Check if the card meets the requirements for this test.
        
        Args:
            card: The card to test
            
        Returns:
            bool: True if requirements are met, False otherwise
        """
        for track_num in self.required_tracks:
            if not card.get_track(track_num):
                return False
        return True
    
    @abstractmethod
    def run_test(self, card) -> TestResult:
        """
        Run the test on the given card.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The test results
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the test to a dictionary.
        
        Returns:
            dict: Dictionary representation of the test
        """
        return {
            'type': self.__class__.__name__,
            'required_tracks': self.required_tracks
        }


class VisaTest(GenericTest):
    """
    Test for Visa credit/debit cards.
    """
    
    def __init__(self):
        """Initialize the Visa test."""
        super().__init__()
        self.add_required_track(2)  # Track 2 is required for Visa cards
    
    def run_test(self, card) -> TestResult:
        """
        Run the Visa card test.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The test results
        """
        result = TestResult()
        
        # Get track 2 data
        track2 = card.get_track(2)
        if not track2:
            return result
        
        track_data = track2.get_chars()
        
        # Visa card numbers start with 4 and are 13, 16, or 19 digits long
        # Try different track formats:
        # Format 1: ;PAN=... (ISO format)
        # Format 2: %B...^... (card-present format)
        
        pan = None
        
        # Try ISO format first (;PAN=...)
        match = re.match(r'^;(\d+)=', track_data)
        if match:
            pan = match.group(1)
        else:
            # Try card-present format (%B...^...)
            match = re.match(r'^%B(\d+)\^', track_data)
            if match:
                pan = match.group(1)
        
        if not pan:
            return result
        
        # Check if it's a valid Visa card number
        if not (len(pan) in [13, 16, 19] and pan.startswith('4')):
            return result
        
        # If we get here, it's probably a Visa card
        result.set_card_type("Visa")
        result.add_tag("Card Number", pan)
        
        # Extract expiration date (YYMM format)
        exp_match = re.search(r'=(\d{2})(\d{2})', track_data)
        if exp_match:
            exp_year = exp_match.group(1)
            exp_month = exp_match.group(2)
            result.add_tag("Expiration", f"20{exp_year}-{exp_month}")
        
        # Extract service code if available
        svc_match = re.search(r'=(?:\d{14,19})(\d{3})', track_data)
        if svc_match:
            service_code = svc_match.group(1)
            result.add_tag("Service Code", service_code)
        
        return result


class MastercardTest(GenericTest):
    """
    Test for Mastercard credit/debit cards.
    """
    
    def __init__(self):
        """Initialize the Mastercard test."""
        super().__init__()
        self.add_required_track(2)  # Track 2 is required for Mastercard
    
    def run_test(self, card) -> TestResult:
        """
        Run the Mastercard test.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The test results
        """
        result = TestResult()
        
        # Get track 2 data
        track2 = card.get_track(2)
        if not track2:
            return result
        
        track_data = track2.get_chars()
        
        # Mastercard numbers start with 51-55 and are 16 digits long
        # Try different track formats
        pan = None
        
        # Try ISO format first (;PAN=...)
        match = re.match(r'^;(\d+)=', track_data)
        if match:
            pan = match.group(1)
        else:
            # Try card-present format (%B...^...)
            match = re.match(r'^%B(\d+)\^', track_data)
            if match:
                pan = match.group(1)
        
        if not pan:
            return result
        
        # Check if it's a valid Mastercard number
        first_two = int(pan[:2])
        if not (51 <= first_two <= 55 and len(pan) == 16):
            return result
        
        # If we get here, it's probably a Mastercard
        result.set_card_type("Mastercard")
        result.add_tag("Card Number", pan)
        
        # Extract expiration date (YYMM format)
        exp_match = re.search(r'=(\d{2})(\d{2})', track_data)
        if exp_match:
            exp_year = exp_match.group(1)
            exp_month = exp_match.group(2)
            result.add_tag("Expiration", f"20{exp_year}-{exp_month}")
        
        # Extract service code if available
        svc_match = re.search(r'=(?:\d{16})(\d{3})', track_data)
        if svc_match:
            service_code = svc_match.group(1)
            result.add_tag("Service Code", service_code)
        
        return result


# Add more card test implementations as needed
# Example: American Express, Discover, etc.


class AmericanExpressTest(GenericTest):
    """
    Test for American Express credit cards.
    American Express cards start with 34 or 37 and are 15 digits long.
    """
    
    def __init__(self):
        """Initialize the American Express test."""
        super().__init__()
        self.add_required_track(2)  # Track 2 is required for AmEx cards
    
    def run_test(self, card) -> TestResult:
        """
        Run the American Express card test.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The test results
        """
        result = TestResult()
        
        # Get track 2 data
        track2 = card.get_track(2)
        if not track2:
            return result
        
        track_data = track2.get_chars()
        
        # American Express card numbers start with 34 or 37 and are 15 digits long
        # Try different track formats
        pan = None
        
        # Try ISO format first (;PAN=...)
        match = re.match(r'^;(\d+)=', track_data)
        if match:
            pan = match.group(1)
        else:
            # Try card-present format (%B...^...)
            match = re.match(r'^%B(\d+)\^', track_data)
            if match:
                pan = match.group(1)
        
        if not pan:
            return result
        
        # Check if it's a valid American Express card number
        is_amex = (pan.startswith('34') or pan.startswith('37')) and len(pan) == 15
        if not is_amex:
            return result
        
        # If we get here, it's probably an American Express card
        result.set_card_type("American Express")
        result.add_tag("Card Number", pan)
        
        # Extract expiration date (YYMM format)
        exp_match = re.search(r'=(\d{2})(\d{2})', track_data)
        if exp_match:
            exp_year = exp_match.group(1)
            exp_month = exp_match.group(2)
            result.add_tag("Expiration", f"20{exp_year}-{exp_month}")
        
        # Extract cardholder name if available (typically after expiration in AmEx)
        name_match = re.search(r'\d{4}([^?]+)\?', track_data)
        if name_match:
            cardholder_name = name_match.group(1).strip()
            if cardholder_name:
                result.add_tag("Cardholder Name", cardholder_name)
        
        return result


class DiscoverTest(GenericTest):
    """
    Test for Discover credit cards.
    Discover card numbers start with 6011, 644-649, or 65 and are 16 digits long.
    """
    
    def __init__(self):
        """Initialize the Discover test."""
        super().__init__()
        self.add_required_track(2)  # Track 2 is required for Discover cards
    
    def run_test(self, card) -> TestResult:
        """
        Run the Discover card test.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The test results
        """
        result = TestResult()
        
        # Get track 2 data
        track2 = card.get_track(2)
        if not track2:
            return result
        
        track_data = track2.get_chars()
        
        # Discover card numbers start with 6011, 644-649, or 65 and are 16 digits long
        # Try different track formats
        pan = None
        
        # Try ISO format first (;PAN=...)
        match = re.match(r'^;(\d+)=', track_data)
        if match:
            pan = match.group(1)
        else:
            # Try card-present format (%B...^...)
            match = re.match(r'^%B(\d+)\^', track_data)
            if match:
                pan = match.group(1)
        
        if not pan:
            return result
        
        # Check if it's a valid Discover card number
        is_discover = (pan.startswith('6011') or 
                      (pan.startswith('65') and len(pan) == 16) or
                      (pan.startswith(('644', '645', '646', '647', '648', '649')) and len(pan) == 16))
        
        if not is_discover:
            return result
        
        # If we get here, it's probably a Discover card
        result.set_card_type("Discover")
        result.add_tag("Card Number", pan)
        
        # Extract expiration date (YYMM format)
        exp_match = re.search(r'=(\d{2})(\d{2})', track_data)
        if exp_match:
            exp_year = exp_match.group(1)
            exp_month = exp_match.group(2)
            result.add_tag("Expiration", f"20{exp_year}-{exp_month}")
        
        # Extract service code if available
        svc_match = re.search(r'=(?:\d{16})(\d{3})', track_data)
        if svc_match:
            service_code = svc_match.group(1)
            result.add_tag("Service Code", service_code)
        
        return result


class JCBCreditTest(GenericTest):
    """
    Test for JCB credit cards.
    JCB card numbers start with 3528-3589 and are 16 digits long.
    """
    
    def __init__(self):
        """Initialize the JCB test."""
        super().__init__()
        self.add_required_track(2)
    
    def run_test(self, card) -> TestResult:
        """
        Run the JCB card test.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The test results
        """
        result = TestResult()
        
        # Get track 2 data
        track2 = card.get_track(2)
        if not track2:
            return result
        
        track_data = track2.get_chars()
        
        # JCB card numbers start with 3528-3589 and are 16 digits long
        # Try different track formats
        pan = None
        
        # Try ISO format first (;PAN=...)
        match = re.match(r'^;(\d+)=', track_data)
        if match:
            pan = match.group(1)
        else:
            # Try card-present format (%B...^...)
            match = re.match(r'^%B(\d+)\^', track_data)
            if match:
                pan = match.group(1)
        
        if not pan:
            return result
        
        # Check if it's a valid JCB card number
        if len(pan) != 16 or not (3528 <= int(pan[:4]) <= 3589):
            return result
        
        # If we get here, it's probably a JCB card
        result.set_card_type("JCB")
        result.add_tag("Card Number", pan)
        
        # Extract expiration date (YYMM format)
        exp_match = re.search(r'=(\d{2})(\d{2})', track_data)
        if exp_match:
            exp_year = exp_match.group(1)
            exp_month = exp_match.group(2)
            result.add_tag("Expiration", f"20{exp_year}-{exp_month}")
        
        return result


class DinersClubTest(GenericTest):
    """
    Test for Diners Club credit cards.
    Diners Club card numbers start with 300-305, 36, or 38-39 and are 14 digits long.
    """
    
    def __init__(self):
        """Initialize the Diners Club test."""
        super().__init__()
        self.add_required_track(2)
    
    def run_test(self, card) -> TestResult:
        """
        Run the Diners Club card test.
        
        Args:
            card: The card to test
            
        Returns:
            TestResult: The test results
        """
        result = TestResult()
        
        # Get track 2 data
        track2 = card.get_track(2)
        if not track2:
            return result
        
        track_data = track2.get_chars()
        
        # Diners Club card numbers start with 300-305, 36, or 38-39 and are 14 digits long
        # Try different track formats
        pan = None
        
        # Try ISO format first (;PAN=...)
        match = re.match(r'^;(\d+)=', track_data)
        if match:
            pan = match.group(1)
        else:
            # Try card-present format (%B...^...)
            match = re.match(r'^%B(\d+)\^', track_data)
            if match:
                pan = match.group(1)
        
        if not pan:
            return result
        
        # Check if it's a valid Diners Club card number
        first_two = pan[:2]
        first_three = pan[:3]
        
        is_diners = ((300 <= int(first_three) <= 305) or 
                    first_two in ('36', '38', '39')) and len(pan) == 14
        
        if not is_diners:
            return result
        
        # If we get here, it's probably a Diners Club card
        result.set_card_type("Diners Club")
        result.add_tag("Card Number", pan)
        
        # Extract expiration date (YYMM format)
        exp_match = re.search(r'=(\d{2})(\d{2})', track_data[match.end():])
        if exp_match:
            exp_year = exp_match.group(1)
            exp_month = exp_match.group(2)
            result.add_tag("Expiration", f"20{exp_year}-{exp_month}")
        
        return result


# Dictionary mapping card type names to test classes
CARD_TESTS = {
    'visa': VisaTest,
    'mastercard': MastercardTest,
    'amex': AmericanExpressTest,
    'discover': DiscoverTest,
    'jcb': JCBCreditTest,
    'diners': DinersClubTest,
}
