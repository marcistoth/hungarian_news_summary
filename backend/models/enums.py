from enum import Enum

class PoliticalLeaning(str, Enum):
    """Enumeration of possible political leanings."""
    LEFT = "bal"
    CENTER_LEFT = "közép-bal"
    CENTER = "közép"
    CENTER_RIGHT = "közép-jobb"
    RIGHT = "jobb"
    
    @classmethod
    def from_string(cls, value: str) -> 'PoliticalLeaning':
        """Convert string to enum, with fallback handling."""
        if not value:
            return cls.CENTER  # Default value
            
        value = value.lower().strip()
        # Map common variations to standard values
        mappings = {
            "baloldali": "bal",
            "bal oldal": "bal",
            "baloldal": "bal",
            "bal-közép": "közép-bal",
            "balközép": "közép-bal",
            "centrum": "közép",
            "középutas": "közép",
            "jobbközép": "közép-jobb",
            "jobb-közép": "közép-jobb",
            "jobboldali": "jobb",
            "jobboldal": "jobb",
        }
        normalized = mappings.get(value, value)
        
        # Try to match to enum
        try:
            return cls(normalized)
        except ValueError:
            # If no match, return default value
            print(f"Warning: Invalid political leaning '{value}', defaulting to 'közép'")
            return cls.CENTER

class Sentiment(str, Enum):
    """Enumeration of possible sentiment values."""
    POSITIVE = "pozitív"
    NEGATIVE = "negatív"
    NEUTRAL = "semleges"
    
    @classmethod
    def from_string(cls, value: str) -> 'Sentiment':
        """Convert string to enum, with fallback handling."""
        if not value:
            return cls.NEUTRAL  # Default value
            
        value = value.lower().strip()
        # Map common variations
        mappings = {
            "pozitiv": "pozitív",
            "positív": "pozitív",
            "positive": "pozitív",
            "negativ": "negatív",
            "negative": "negatív",
            "semleges": "semleges",
            "neutral": "semleges",
            "neutrális": "semleges",
        }
        normalized = mappings.get(value, value)
        
        # Try to match to enum
        try:
            return cls(normalized)
        except ValueError:
            # If no match, return default value
            print(f"Warning: Invalid sentiment '{value}', defaulting to 'semleges'")
            return cls.NEUTRAL