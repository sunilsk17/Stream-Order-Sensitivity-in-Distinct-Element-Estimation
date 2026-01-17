"""
KMV (K-Minimum Values) - Cardinality Estimation Algorithm

Implementation of the K-Minimum Values algorithm for cardinality estimation.
Also known as 'Min-Count Sketch' or 'K-minimum hash values'.

Key characteristics:
- Maintains k smallest hash values seen
- Simple, deterministic, and mergeable
- Provides accurate cardinality estimates
- Better theoretical guarantees than random sampling
"""

import mmh3
import math


class KMVSketch:
    """
    K-Minimum Values sketch for cardinality estimation.
    
    Maintains the k smallest hash values from the input stream.
    Cardinality is estimated based on the k-th smallest hash and total items seen.
    
    Args:
        k: Number of minimum values to retain (typically 256, 512, 1024, etc.)
           Larger k -> more memory, lower error
    """
    
    def __init__(self, k=512):
        """
        Initialize KMV Sketch.
        
        Args:
            k: Number of minimum hash values to keep
               Default 512 gives comparable accuracy to HLL with p=10
        """
        if k <= 0:
            raise ValueError("k must be positive")
        
        self.k = k
        self.min_values = []  # Sorted list of minimum hash values
        self.n = 0  # Total number of items added
        self.max_hash = 2 ** 64  # Maximum hash value (for normalization)
    
    def add(self, item):
        """
        Add an item to the sketch.
        
        Args:
            item: Hashable object (typically string)
        """
        # Hash the item using MurmurHash (64-bit unsigned)
        h = mmh3.hash64(str(item), signed=False)[0]
        
        self.n += 1
        
        # Only consider if we don't have k items yet, or if hash is smaller than max
        if len(self.min_values) < self.k:
            self.min_values.append(h)
            self.min_values.sort()
        elif h < self.min_values[-1]:
            # Replace largest minimum with this smaller value
            self.min_values[-1] = h
            self.min_values.sort()
    
    def cardinality(self):
        """
        Estimate the number of distinct elements.
        
        Returns:
            Estimated cardinality (float)
        """
        if len(self.min_values) == 0:
            return 0.0
        
        if len(self.min_values) < self.k:
            # If we haven't filled k slots, return exact count (lower bound)
            return float(self.n)
        
        # Get the k-th minimum value
        k_min = self.min_values[-1]
        
        # Cardinality estimate: ratio of hash space
        # If k smallest hash values span [0, k_min], then cardinality ~ k / (k_min / MAX_HASH)
        # Which simplifies to: k * MAX_HASH / k_min
        
        if k_min == 0:
            # Edge case: k_min is 0, estimate based on n
            return float(self.n)
        
        # Normalized form: estimate = k / (k_min / MAX_HASH)
        # But we use: estimate = (k - 0.5) * MAX_HASH / k_min for better accuracy
        estimate = (self.k - 0.5) * self.max_hash / float(k_min)
        
        return estimate
    
    def cardinality_with_confidence(self):
        """
        Estimate cardinality with confidence interval.
        
        Returns:
            Tuple of (estimate, lower_bound, upper_bound)
        """
        estimate = self.cardinality()
        
        # Standard error is approximately sqrt(C^2 / k)
        # For 95% confidence interval: ±1.96 * standard_error
        if self.k > 0:
            # Using relationship from KMV theory
            std_error = estimate / math.sqrt(self.k) * 0.5  # Empirical constant
            margin = 1.96 * std_error
            
            lower = max(float(self.k), estimate - margin)
            upper = estimate + margin
            
            return estimate, lower, upper
        else:
            return estimate, estimate, estimate
    
    def get_min_values(self):
        """Return the k minimum hash values (for analysis)."""
        return self.min_values[:]
    
    def get_statistics(self):
        """Return sketch statistics."""
        return {
            'k': self.k,
            'n_items_processed': self.n,
            'min_values_retained': len(self.min_values),
            'max_of_minimums': self.min_values[-1] if self.min_values else None,
            'min_of_minimums': self.min_values[0] if self.min_values else None,
        }
    
    def merge(self, other):
        """
        Merge another KMV Sketch into this one.
        
        Args:
            other: Another KMVSketch instance (must have same k)
        
        Returns:
            New merged KMVSketch
        """
        if not isinstance(other, KMVSketch):
            raise TypeError("Can only merge with another KMVSketch")
        
        if self.k != other.k:
            raise ValueError(f"Cannot merge sketches with different k values: {self.k} vs {other.k}")
        
        # Create new sketch
        merged = KMVSketch(k=self.k)
        
        # Combine all minimum values from both sketches
        combined = sorted(set(self.min_values + other.min_values))
        
        # Keep only the k smallest
        merged.min_values = combined[:self.k]
        merged.n = self.n + other.n
        
        return merged


class KMVUnion:
    """
    KMV Union operator for merging multiple sketches.
    
    Maintains k smallest values across all sketches added.
    """
    
    def __init__(self, k=512):
        """
        Initialize Union.
        
        Args:
            k: Number of minimum values (must match individual sketches)
        """
        self.k = k
        self.min_values = []
        self.max_hash = 2 ** 64
    
    def update(self, sketch):
        """
        Add a sketch to the union.
        
        Args:
            sketch: KMVSketch instance to add
        """
        if not isinstance(sketch, KMVSketch):
            raise TypeError("Can only update with KMVSketch")
        
        if sketch.k != self.k:
            raise ValueError(f"Cannot merge sketches with different k: {sketch.k} vs {self.k}")
        
        # Add all minimum values from sketch
        self.min_values.extend(sketch.min_values)
        self.min_values.sort()
        
        # Keep only k smallest
        self.min_values = self.min_values[:self.k]
    
    def get_result(self):
        """
        Get the union as a KMV Sketch.
        
        Returns:
            KMVSketch with merged results
        """
        result = KMVSketch(k=self.k)
        result.min_values = self.min_values[:self.k]
        return result
    
    def cardinality(self):
        """Estimate cardinality of the union."""
        if len(self.min_values) == 0:
            return 0.0
        
        if len(self.min_values) < self.k:
            return float(len(self.min_values))
        
        k_min = self.min_values[-1]
        
        if k_min == 0:
            return float(self.k)
        
        estimate = (self.k - 0.5) * self.max_hash / float(k_min)
        return estimate
