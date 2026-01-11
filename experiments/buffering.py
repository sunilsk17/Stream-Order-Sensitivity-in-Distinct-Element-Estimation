"""
Order-Robust Buffering Strategy.

Proposes a lightweight buffering mechanism to mitigate order sensitivity.
Idea: Buffer items and shuffle before adding to sketch to decorrelate temporal patterns.
"""

import random
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sketches.hll import HyperLogLog
from sketches.fm import FlajoletMartin


class BufferedHLL:
    """
    HyperLogLog with order-robust buffering.
    
    Maintains a small buffer of items. When buffer reaches threshold,
    items are randomly shuffled before being added to the underlying HLL.
    This decorrelates temporal patterns in the input stream.
    """
    
    def __init__(self, p=10, buffer_size=500):
        """
        Initialize buffered HLL.
        
        Args:
            p: HLL precision parameter
            buffer_size: Size of the buffer (typically 1-5% of HLL memory)
        """
        self.hll = HyperLogLog(p=p)
        self.buffer = []
        self.buffer_size = buffer_size
        self.p = p
        self.flushes = 0
    
    def add(self, item):
        """Add item to buffer. Flush when buffer is full."""
        self.buffer.append(item)
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        """Shuffle buffer contents and add to underlying HLL."""
        random.shuffle(self.buffer)
        for item in self.buffer:
            self.hll.add(item)
        self.buffer.clear()
        self.flushes += 1
    
    def count(self):
        """Get cardinality estimate (flushes remaining buffer)."""
        if self.buffer:
            self.flush()
        return self.hll.count()
    
    def get_stats(self):
        """Return buffering statistics."""
        return {
            'buffer_size': self.buffer_size,
            'flushes': self.flushes,
            'current_buffer_items': len(self.buffer)
        }


class BufferedFM:
    """
    Flajolet-Martin with order-robust buffering.
    """
    
    def __init__(self, num_hashes=64, buffer_size=500):
        """
        Initialize buffered FM.
        
        Args:
            num_hashes: Number of hash functions
            buffer_size: Size of the buffer
        """
        self.fm = FlajoletMartin(num_hashes=num_hashes)
        self.buffer = []
        self.buffer_size = buffer_size
        self.num_hashes = num_hashes
        self.flushes = 0
    
    def add(self, item):
        """Add item to buffer. Flush when buffer is full."""
        self.buffer.append(item)
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self):
        """Shuffle buffer contents and add to underlying FM."""
        random.shuffle(self.buffer)
        for item in self.buffer:
            self.fm.add(item)
        self.buffer.clear()
        self.flushes += 1
    
    def count(self):
        """Get cardinality estimate (flushes remaining buffer)."""
        if self.buffer:
            self.flush()
        return self.fm.count()
    
    def get_stats(self):
        """Return buffering statistics."""
        return {
            'buffer_size': self.buffer_size,
            'flushes': self.flushes,
            'current_buffer_items': len(self.buffer)
        }


def load_stream(filepath):
    """Load stream from file."""
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]


def compare_buffering_strategies(stream_path, num_runs=5):
    """
    Compare buffered vs non-buffered sketches on grouped data.
    
    Tests the hypothesis that buffering improves robustness to
    structured/correlated input orders.
    """
    stream = load_stream(stream_path)
    true_count = len(set(stream))
    
    # Create grouped (bursty) order
    grouped = []
    unique_items = list(set(stream))[:50]  # Group first 50 unique items heavily
    for item in unique_items:
        grouped.extend([item] * (stream.count(item)))
    for item in stream:
        if item not in grouped:
            grouped.append(item)
    grouped = grouped[:len(stream)]
    
    print(f"{'='*70}")
    print(f"EXPERIMENT: Order-Robust Buffering Strategy")
    print(f"{'='*70}")
    print(f"Stream size: {len(stream)} elements")
    print(f"True cardinality: {true_count} unique elements")
    print(f"Testing on GROUPED (worst-case) order to isolate buffering effect")
    print(f"Number of runs: {num_runs}\n")
    
    # Test different buffer sizes
    buffer_sizes = [100, 500, 1000, 2000]
    results = {}
    
    for buf_size in buffer_sizes:
        print(f"Buffer size: {buf_size} items")
        print("-" * 50)
        
        hll_errors = []
        buffered_hll_errors = []
        fm_errors = []
        buffered_fm_errors = []
        
        for run in range(num_runs):
            # Standard HLL
            hll = HyperLogLog(p=10)
            for item in grouped:
                hll.add(item)
            hll_est = hll.count()
            hll_errors.append(abs(hll_est - true_count) / true_count)
            
            # Buffered HLL
            buf_hll = BufferedHLL(p=10, buffer_size=buf_size)
            for item in grouped:
                buf_hll.add(item)
            buf_hll_est = buf_hll.count()
            buffered_hll_errors.append(abs(buf_hll_est - true_count) / true_count)
            
            # Standard FM
            fm = FlajoletMartin(num_hashes=64)
            for item in grouped:
                fm.add(item)
            fm_est = fm.count()
            fm_errors.append(abs(fm_est - true_count) / true_count)
            
            # Buffered FM
            buf_fm = BufferedFM(num_hashes=64, buffer_size=buf_size)
            for item in grouped:
                buf_fm.add(item)
            buf_fm_est = buf_fm.count()
            buffered_fm_errors.append(abs(buf_fm_est - true_count) / true_count)
        
        # Statistics
        hll_mean_error = sum(hll_errors) / len(hll_errors)
        buf_hll_mean_error = sum(buffered_hll_errors) / len(buffered_hll_errors)
        fm_mean_error = sum(fm_errors) / len(fm_errors)
        buf_fm_mean_error = sum(buffered_fm_errors) / len(buffered_fm_errors)
        
        hll_std = (sum((e - hll_mean_error) ** 2 for e in hll_errors) / len(hll_errors)) ** 0.5
        buf_hll_std = (sum((e - buf_hll_mean_error) ** 2 for e in buffered_hll_errors) / len(buffered_hll_errors)) ** 0.5
        fm_std = (sum((e - fm_mean_error) ** 2 for e in fm_errors) / len(fm_errors)) ** 0.5
        buf_fm_std = (sum((e - buf_fm_mean_error) ** 2 for e in buffered_fm_errors) / len(buffered_fm_errors)) ** 0.5
        
        results[buf_size] = {
            'hll': {'mean_error': hll_mean_error, 'std': hll_std},
            'buffered_hll': {'mean_error': buf_hll_mean_error, 'std': buf_hll_std},
            'fm': {'mean_error': fm_mean_error, 'std': fm_std},
            'buffered_fm': {'mean_error': buf_fm_mean_error, 'std': buf_fm_std}
        }
        
        improvement_hll = (hll_mean_error - buf_hll_mean_error) / hll_mean_error * 100 if hll_mean_error > 0 else 0
        improvement_fm = (fm_mean_error - buf_fm_mean_error) / fm_mean_error * 100 if fm_mean_error > 0 else 0
        
        print(f"HyperLogLog:")
        print(f"  Standard:     {hll_mean_error*100:.2f}% ± {hll_std*100:.2f}%")
        print(f"  Buffered:     {buf_hll_mean_error*100:.2f}% ± {buf_hll_std*100:.2f}%")
        print(f"  Improvement:  {improvement_hll:.1f}%\n")
        
        print(f"Flajolet-Martin:")
        print(f"  Standard:     {fm_mean_error*100:.2f}% ± {fm_std*100:.2f}%")
        print(f"  Buffered:     {buf_fm_mean_error*100:.2f}% ± {buf_fm_std*100:.2f}%")
        print(f"  Improvement:  {improvement_fm:.1f}%\n")
    
    return results


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    stream_path = os.path.join(project_root, "data", "stream.txt")
    
    # Check if stream exists
    if not os.path.exists(stream_path):
        print(f"Stream file not found. Generating synthetic stream...")
        os.chdir(os.path.join(project_root, "data"))
        from generate_stream import generate_synthetic_stream
        generate_synthetic_stream()
        stream_path = os.path.join(project_root, "data", "stream.txt")
    
    results = compare_buffering_strategies(stream_path, num_runs=5)
