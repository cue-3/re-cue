"""
Test file for ty Language Server Protocol integration
This file contains various Python patterns to test ty LSP features
"""

from typing import List, Dict, Optional


# Test 1: Basic type annotations
def greet(name: str) -> str:
    """Simple function with type hints."""
    return f"Hello, {name}!"


# Test 2: Type errors - should show diagnostics
def add_numbers(a: int, b: int) -> int:
    """This should work fine."""
    return a + b


def broken_add(a: int, b: int) -> int:
    """This should show an error - returning string instead of int."""
    return "not a number"  # Type error: returning str instead of int


# Test 3: Missing type hints - ty should warn
def no_types(x, y):
    """Function without type annotations."""
    return x + y


# Test 4: Optional types
def find_user(user_id: int) -> Optional[Dict[str, str]]:
    """Returns user dict or None."""
    if user_id > 0:
        return {"name": "Test User", "email": "test@example.com"}
    return None


# Test 5: List annotations
def process_names(names: List[str]) -> List[str]:
    """Process a list of names."""
    return [name.upper() for name in names]


# Test 6: Type mismatch - should show error
def wrong_type_usage():
    """Using wrong types."""
    numbers: List[int] = [1, 2, 3]
    numbers.append("string")  # Type error: str not compatible with int


# Test 7: Class with type hints
class User:
    """User class with typed attributes."""
    
    def __init__(self, name: str, age: int) -> None:
        self.name: str = name
        self.age: int = age
    
    def get_info(self) -> Dict[str, any]:
        """Get user information."""
        return {"name": self.name, "age": self.age}


# Test 8: Generic types
from typing import TypeVar, Generic

T = TypeVar('T')

class Container(Generic[T]):
    """Generic container class."""
    
    def __init__(self, value: T) -> None:
        self.value = value
    
    def get(self) -> T:
        return self.value


# Test function calls to see hover information
if __name__ == "__main__":
    # Hover over these to see type information
    result = greet("World")
    numbers_sum = add_numbers(5, 10)
    user = find_user(123)
    
    # This should show error
    container: Container[int] = Container(42)
    wrong_container: Container[int] = Container("string")  # Type error
