"""
Theta Sketch - Cardinality Estimation Algorithm

Implementation of the Theta Sketch algorithm for cardinality estimation.
Based on Apache DataSketches library principles.

Key characteristics:
- Maintains a set of sketch entries with hash values
- Uses theta (sampling probability) to maintain size
- More accurate than HLL for small cardinalities
- Better memory efficiency through dynamic sampling
"""

import mmh3
import math


class ThetaSketch:
    """
    Theta Sketch cardinality estimator.
    
    Maintains a set of sampled hash values. Uses a theta value (threshold) to 
    maintain a constant-size sketch. Items with hash values less than theta 
    are retained in the sketch.
    
    Args:
        k: Nominal entries (size of the sketch). Default 4096 gives ~2% error.
    """
    
    def __init__(self, k=4096):
        """
        Initialize Theta Sketch.
        
        Args:
            k: Nominal number of entries in sketch (must be power of 2)
               Larger k -> more memory, lower error
               Default 4096 matches typical HLL usage
        """
        if k & (k - 1) != 0:
            raise ValueError(f"k={k} must be a power of 2")
        
        self.k = k
        self.entries = set()  # Set of (hash_value, item) tuples
        self.theta = 1.0  # Initially accept all items
        self.num_retained = 0  # Number of entries kept
        self.is_empty = True
        
        # Estimator accuracy constant
        self.c = 2.0  # Empirically determined constant
    
    def add(self, item):
        """
        Add an item to the sketch.
        
        Args:
            item: Hashable object (typically string)
        """
        # Hash the item using MurmurHash (64-bit)
        h = mmh3.hash64(str(item), signed=False)[0]
        
        # Normalize hash to [0, 1) range
        hash_value = h / (2 ** 64)
        
        # Only add if hash is below theta threshold
        if hash_value < self.theta:
            self.entries.add((hash_value, str(item)))
            self.num_retained = len(self.entries)
            self.is_empty = False
            
            # Resize if entries exceed k
            if self.num_retained > self.k:
                self._resize()
    
    def _resize(self):
        """
        Reduce sketch size to k entries by updating theta.
        Keeps entries with lowest hash values.
        """
        if len(self.entries) > self.k:
            # Sort by hash value and keep the k entries with smallest hashes
            sorted_entries = sorted(self.entries, key=lambda x: x[0])
            self.entries = set(sorted_entries[:self.k])
            
            # Update theta to next largest hash value not in sketch
            if len(self.entries) == self.k and len(sorted_entries) > self.k:
                self.theta = sorted_entries[self.k][0]
            
            self.num_retained = len(self.entries)
    
    def cardinality(self):
        """
        Estimate the number of distinct elements.
        
        Returns:
            Estimated cardinality (float)
        """
        if self.is_empty:
            return 0.0
        
        # Number of retained entries
        count = len(self.entries)
        
        if count == 0:
            return 0.0
        
        # Theta-based estimation
        # If all k entries are retained, estimate based on sampling threshold
        if count < self.k and self.theta < 1.0:
            # Extrapolate based on sampling probability
            estimate = count / self.theta
        else:
            # All slots filled, use theta value for estimation
            if self.theta > 0:
                estimate = self.k / self.theta
            else:
                estimate = float('inf')
        
        return estimate
    
    def get_entries(self):
        """Return current entries (for debugging/analysis)."""
        return list(self.entries)
    
    def get_theta(self):
        """Return current theta value."""
        return self.theta
    
    def merge(self, other):
        """
        Merge another Theta Sketch into this one.
        
        Args:
            other: Another ThetaSketch instance
        
        Returns:
            Merged ThetaSketch
        """
        if not isinstance(other, ThetaSketch):
            raise TypeError("Can only merge with another ThetaSketch")
        
        # Create new sketch
        merged = ThetaSketch(k=self.k)
        
        # Add entries from both sketches
        for hash_val, item in self.entries:
            merged.entries.add((hash_val, item))
        
        for hash_val, item in other.entries:
            merged.entries.add((hash_val, item))
        
        # Update theta to minimum
        merged.theta = min(self.theta, other.theta)
        
        # Resize if necessary
        if len(merged.entries) > self.k:
            merged._resize()
        
        merged.num_retained = len(merged.entries)
        merged.is_empty = (len(merged.entries) == 0)
        
        return merged


class ThetaSketchUnion:
    """
    Theta Sketch Union operator for merging multiple sketches.
    
    Efficiently combines multiple Theta Sketches while maintaining accuracy.
    """
    
    def __init__(self, k=4096):
        """
        Initialize Union.
        
        Args:
            k: Nominal number of entries (must match individual sketches)
        """
        self.k = k
        self.entries = set()
        self.theta = 1.0
    
    def update(self, sketch):
        """
        Add a sketch to the union.
        
        Args:
            sketch: ThetaSketch instance to add
        """
        if not isinstance(sketch, ThetaSketch):
            raise TypeError("Can only update with ThetaSketch")
        
        # Add all entries that are below combined theta
        for hash_val, item in sketch.entries:
            if hash_val < self.theta:
                self.entries.add((hash_val, item))
        
        # Update theta
        self.theta = min(self.theta, sketch.theta)
        
        # Resize if necessary
        if len(self.entries) > self.k:
            self._resize()
    
    def _resize(self):
        """Reduce to k entries."""
        if len(self.entries) > self.k:
            sorted_entries = sorted(self.entries, key=lambda x: x[0])
            self.entries = set(sorted_entries[:self.k])
            
            if len(self.entries) == self.k and len(sorted_entries) > self.k:
                self.theta = sorted_entries[self.k][0]
    
    def get_result(self):
        """
        Get the union as a Theta Sketch.
        
        Returns:
            ThetaSketch with merged results
        """
        result = ThetaSketch(k=self.k)
        result.entries = self.entries.copy()
        result.theta = self.theta
        result.num_retained = len(self.entries)
        result.is_empty = (len(self.entries) == 0)
        return result
    
    def cardinality(self):
        """Estimate cardinality of the union."""
        if len(self.entries) == 0:
            return 0.0
        
        if len(self.entries) < self.k and self.theta < 1.0:
            return len(self.entries) / self.theta
        else:
            if self.theta > 0:
                return self.k / self.theta
            else:
                return float('inf')
