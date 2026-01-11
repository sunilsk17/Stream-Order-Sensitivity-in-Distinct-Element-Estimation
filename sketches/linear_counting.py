"""
Linear Counting sketch for distinct cardinality estimation.

Simpler than HyperLogLog, uses bitmap approach.
Used to validate that order sensitivity is universal, not specific to HLL.
"""

import sys
import os
import mmh3
from math import log

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class LinearCounting:
    """
    Linear Counting sketch for cardinality estimation.
    
    Simple bitmap-based approach:
    - Hash each element to one of m positions
    - Track which positions were seen
    - Estimate: -m * ln(1 - X/m) where X = number of occupied positions
    
    Theory: Should show similar order sensitivity to HLL
    """
    
    def __init__(self, m=16384):
        """
        Initialize Linear Counting.
        m: number of bits in the bitmap (default 16384)
        """
        self.m = m
        self.bitmap = set()  # Use set for efficiency
        
    def add(self, element):
        """Add element to the sketch."""
        # Hash to uniform position
        hash_value = mmh3.hash(str(element), seed=0)
        position = abs(hash_value) % self.m
        self.bitmap.add(position)
    
    def count(self):
        """Estimate cardinality using Linear Counting formula."""
        X = len(self.bitmap)  # Number of occupied positions
        
        if X == 0:
            return 0
        
        # Linear Counting formula: -m * ln(1 - X/m)
        ratio = X / self.m
        if ratio >= 1.0:
            # All positions occupied - need larger m
            return self.m * log(self.m)  # Fallback estimate
        
        try:
            estimate = -self.m * log(1 - ratio)
            return estimate
        except:
            # Safety fallback
            return self.m
    
    def merge(self, other):
        """Merge with another Linear Counting sketch."""
        if self.m != other.m:
            raise ValueError("Cannot merge sketches with different m")
        self.bitmap.update(other.bitmap)
    
    def __repr__(self):
        return f"LinearCounting(m={self.m}, occupied={len(self.bitmap)})"


if __name__ == "__main__":
    # Quick test
    lc = LinearCounting()
    for i in range(100):
        lc.add(f"item_{i}")
    
    estimate = lc.count()
    print(f"Added 100 unique items, estimate: {estimate:.0f}")
    print(f"Error: {abs(estimate - 100) / 100 * 100:.2f}%")
