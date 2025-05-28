"""
Card class for managing magstripe card data and tracks
"""

from typing import Dict, Optional
from track import Track

class Card:
    """
    Represents a magstripe card with multiple tracks
    """
    
    # Track presence indicators
    UNKNOWN = 0  # Reader didn't support this track
    PRESENT = 1  # Track is present and readable
    MISSING = 2  # Track is not present
    
    def __init__(self):
        """Initialize a new Card instance"""
        self.tracks: Dict[int, Track] = {}  # track_num: Track
        self.track_presence: Dict[int, int] = {}  # track_num: presence_status
    
    def has_track(self, track_num: int) -> int:
        """
        Check if a track is present on the card
        
        Args:
            track_num: The track number to check
            
        Returns:
            int: PRESENT if track exists, MISSING if not, UNKNOWN if not checked
        """
        return self.track_presence.get(track_num, self.UNKNOWN)
    
    def add_missing_track(self, track_num: int) -> None:
        """
        Mark a track as missing
        
        Args:
            track_num: The track number that is missing
        """
        self.track_presence[track_num] = self.MISSING
    
    def add_track(self, track: Track) -> None:
        """
        Add a track to the card
        
        Args:
            track: The Track object to add
        """
        track_num = track.get_number()
        self.tracks[track_num] = track
        self.track_presence[track_num] = self.PRESENT
    
    def get_track(self, track_num: int) -> Optional[Track]:
        """
        Get a track by number
        
        Args:
            track_num: The track number to retrieve
            
        Returns:
            Optional[Track]: The Track object if found, None otherwise
        """
        return self.tracks.get(track_num)
    
    def decode_tracks(self) -> None:
        """Decode all tracks on the card"""
        for track in self.tracks.values():
            track.decode()
    
    def print_tracks(self) -> None:
        """Print information about all tracks on the card"""
        if not self.tracks:
            print("No tracks found on card")
            return
            
        print("\nCard Tracks:")
        print("-" * 50)
        
        for track_num in sorted(self.tracks.keys()):
            track = self.tracks[track_num]
            status = "Present" if self.has_track(track_num) == self.PRESENT else "Missing"
            print(f"Track {track_num} ({status}): {track.get_chars()}")
            
            # Print fields if available
            num_fields = track.get_num_fields()
            if num_fields > 0:
                print(f"  Fields (total {num_fields}):")
                for i in range(num_fields):
                    field = track.get_field(i)
                    print(f"    {i+1}. {field}")
            
            print("-" * 50)
    
    def to_dict(self) -> dict:
        """
        Convert card data to a dictionary
        
        Returns:
            dict: Dictionary representation of the card
        """
        return {
            'tracks': {num: track.to_dict() for num, track in self.tracks.items()},
            'track_presence': self.track_presence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        """
        Create a Card instance from a dictionary
        
        Args:
            data: Dictionary containing card data
            
        Returns:
            Card: A new Card instance
        """
        card = cls()
        # Implementation would create Track objects from the dict data
        return card
