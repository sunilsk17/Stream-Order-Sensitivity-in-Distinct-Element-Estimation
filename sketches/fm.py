import mmh3
import math

class FlajoletMartin:
    """
    Flajolet-Martin (FM) distinct count sketch.
    
    Early probabilistic algorithm for cardinality estimation.
    Maintains only the position of the first 1 bit seen so far.
    Has higher variance than HyperLogLog but simpler to understand.
    """
    
    def __init__(self, num_hashes=64):
        """
        Initialize Flajolet-Martin sketch.
        
        Args:
            num_hashes: Number of independent hash functions to use (for better accuracy)
        """
        self.max_zero = [0] * num_hashes
        self.num_hashes = num_hashes
    
    def add(self, item):
        """
        Add an item to the sketch.
        
        Args:
            item: Hashable object (typically string)
        """
        item_str = str(item)
        
        for i in range(self.num_hashes):
            # Create independent hash functions using different seeds
            h = mmh3.hash(item_str, seed=i, signed=False)
            
            if h == 0:
                # Special case: hash is 0, so leading zero count is infinite
                trailing = 33
            else:
                # Count trailing zeros (position of first 1 bit from right)
                # This is the number of consecutive 0s at the end
                trailing = (h & -h).bit_length() - 1
            
            # Update maximum position of first 1 bit
            self.max_zero[i] = max(self.max_zero[i], trailing)
    
    def count(self):
        """
        Estimate the number of distinct elements.
        
        Uses multiple hash functions and averages estimates.
        
        Returns:
            Estimated cardinality
        """
        # Compute estimate for each hash function
        estimates = []
        for max_z in self.max_zero:
            if max_z == 0:
                # No trailing zeros seen means likely small cardinality
                estimates.append(1.0)
            else:
                # Cardinality estimate: 2^(max position of first 1 bit)
                estimates.append(2.0 ** max_z)
        
        # Average estimates for better accuracy
        avg_estimate = sum(estimates) / len(estimates)
        
        # Bias correction factor (empirical)
        correction_factor = 0.77351
        return avg_estimate * correction_factor
    
    def get_max_zeros(self):
        """Return current state of max zero positions (for debugging)."""
        return self.max_zero[:]
