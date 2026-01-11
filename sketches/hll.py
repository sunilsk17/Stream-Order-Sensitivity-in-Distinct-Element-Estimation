import mmh3
import math

class HyperLogLog:
    def __init__(self, p=10):
        """
        Initialize HyperLogLog sketch.
        
        Args:
            p: Precision parameter (number of bits for register index)
               Larger p -> more registers -> lower error, more memory
        """
        self.p = p
        self.m = 1 << p  # 2^p registers
        self.registers = [0] * self.m
        
        # Alpha constant based on number of registers
        if self.m == 16:
            self.alpha = 0.673
        elif self.m == 32:
            self.alpha = 0.697
        elif self.m == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1 + 1.079 / self.m)
    
    def _leading_zero_count(self, w):
        """
        Count leading zeros + 1 in the bits after the first p bits.
        This is rho: position of first 1 bit (+ 1 for w=0 case).
        """
        if w == 0:
            return 64 - self.p + 1
        # Count leading zero bits
        return (64 - self.p) - w.bit_length() + 1
    
    def add(self, item):
        """
        Add an item to the sketch.
        
        Args:
            item: Hashable object (typically string)
        """
        # Hash the item using MurmurHash
        h = mmh3.hash64(str(item), signed=False)[0]
        
        # Extract register index from first p bits
        idx = h >> (64 - self.p)
        
        # Get remaining 64-p bits
        w = h & ((1 << (64 - self.p)) - 1)
        
        # Update register with maximum rho value
        rho = self._leading_zero_count(w)
        self.registers[idx] = max(self.registers[idx], rho)
    
    def count(self):
        """
        Estimate the number of distinct elements.
        
        Returns:
            Estimated cardinality
        """
        # Standard HLL cardinality estimation
        Z = sum(2.0 ** (-r) for r in self.registers)
        E = self.alpha * self.m * self.m / Z
        
        # Small range correction
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V != 0:
                E = self.m * math.log(self.m / float(V))
        # Large range correction
        elif E > (1.0/30.0) * (1 << 32):
            arg = 1.0 - E / (1 << 32)
            if arg > 0:
                E = -1 * (1 << 32) * math.log(arg)
        
        return E
    
    def get_registers(self):
        """Return current register state (for debugging/analysis)."""
        return self.registers[:]
