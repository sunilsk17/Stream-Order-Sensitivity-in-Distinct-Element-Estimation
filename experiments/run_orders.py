"""
Main experiment: Test HyperLogLog and Flajolet-Martin under different stream orders.

This script demonstrates the core hypothesis:
Identical datasets processed in different orders produce different estimation errors.
"""

import random
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sketches.hll import HyperLogLog
from sketches.fm import FlajoletMartin


def load_stream(filepath):
    """Load stream from file."""
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]


def run_hll(stream, p=10):
    """Run HyperLogLog on stream."""
    hll = HyperLogLog(p=p)
    for item in stream:
        hll.add(item)
    return hll.count()


def run_fm(stream, num_hashes=64):
    """Run Flajolet-Martin on stream."""
    fm = FlajoletMartin(num_hashes=num_hashes)
    for item in stream:
        fm.add(item)
    return fm.count()


def generate_stream_orders(stream):
    """
    Generate multiple ordering variants of the same stream.
    
    Returns:
        dict: Named variants of the stream
    """
    orders = {}
    
    # 1. Original order
    orders['original'] = stream[:]
    
    # 2. Fully randomized order
    shuffled = stream[:]
    random.shuffle(shuffled)
    orders['random'] = shuffled
    
    # 3. Chunk-shuffled (shuffle within fixed-size chunks)
    chunked = []
    chunk_size = 1000
    for i in range(0, len(stream), chunk_size):
        chunk = stream[i:i + chunk_size]
        random.shuffle(chunk)
        chunked.extend(chunk)
    orders['chunk_shuffled'] = chunked
    
    # 4. Grouped order (simulate bursty/correlated data)
    # Simple approach: sort by item name to create grouping
    grouped = sorted(stream)
    orders['grouped'] = grouped
    
    return orders


def run_experiment(stream_path, num_runs=5):
    """
    Run complete experiment across all stream orderings.
    
    Args:
        stream_path: Path to input stream file
        num_runs: Number of times to run each variant (for variance analysis)
    """
    # Load stream
    stream = load_stream(stream_path)
    true_count = len(set(stream))
    
    print(f"{'='*70}")
    print(f"EXPERIMENT: Stream Order Sensitivity in Distinct Element Sketches")
    print(f"{'='*70}")
    print(f"Stream size: {len(stream)} elements")
    print(f"True cardinality: {true_count} unique elements")
    print(f"Number of runs per variant: {num_runs}")
    print(f"{'='*70}\n")
    
    # Generate stream variants
    orders = generate_stream_orders(stream)
    
    results = {}
    
    for order_name, ordered_stream in orders.items():
        print(f"Testing: {order_name.upper()}")
        print("-" * 50)
        
        hll_estimates = []
        fm_estimates = []
        
        for run in range(num_runs):
            # Run HLL
            hll_est = run_hll(ordered_stream, p=10)
            hll_estimates.append(hll_est)
            
            # Run FM
            fm_est = run_fm(ordered_stream, num_hashes=64)
            fm_estimates.append(fm_est)
        
        # Compute statistics
        hll_mean = sum(hll_estimates) / len(hll_estimates)
        hll_errors = [abs(est - true_count) / true_count for est in hll_estimates]
        hll_mean_error = sum(hll_errors) / len(hll_errors)
        hll_variance = sum((err - hll_mean_error) ** 2 for err in hll_errors) / len(hll_errors)
        
        fm_mean = sum(fm_estimates) / len(fm_estimates)
        fm_errors = [abs(est - true_count) / true_count for est in fm_estimates]
        fm_mean_error = sum(fm_errors) / len(fm_errors)
        fm_variance = sum((err - fm_mean_error) ** 2 for err in fm_errors) / len(fm_errors)
        
        results[order_name] = {
            'hll': {
                'estimates': hll_estimates,
                'mean': hll_mean,
                'mean_error': hll_mean_error,
                'variance': hll_variance,
                'stdev': hll_variance ** 0.5
            },
            'fm': {
                'estimates': fm_estimates,
                'mean': fm_mean,
                'mean_error': fm_mean_error,
                'variance': fm_variance,
                'stdev': fm_variance ** 0.5
            }
        }
        
        # Print results
        print(f"HyperLogLog (p=10):")
        print(f"  Mean estimate:    {hll_mean:.1f}")
        print(f"  Mean rel. error:  {hll_mean_error*100:.2f}%")
        print(f"  Error std. dev.:  {results[order_name]['hll']['stdev']*100:.2f}%")
        
        print(f"Flajolet-Martin (64 hashes):")
        print(f"  Mean estimate:    {fm_mean:.1f}")
        print(f"  Mean rel. error:  {fm_mean_error*100:.2f}%")
        print(f"  Error std. dev.:  {results[order_name]['fm']['stdev']*100:.2f}%")
        print()
    
    # Summary comparison
    print(f"{'='*70}")
    print("SUMMARY: Order Sensitivity Analysis")
    print(f"{'='*70}\n")
    
    print("HyperLogLog mean relative errors across orders:")
    for order_name in orders.keys():
        error = results[order_name]['hll']['mean_error']
        print(f"  {order_name:20s}: {error*100:.2f}%")
    
    print("\nFlajolet-Martin mean relative errors across orders:")
    for order_name in orders.keys():
        error = results[order_name]['fm']['mean_error']
        print(f"  {order_name:20s}: {error*100:.2f}%")
    
    return results


if __name__ == "__main__":
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    stream_path = os.path.join(project_root, "data", "stream.txt")
    
    # Check if stream exists
    if not os.path.exists(stream_path):
        print(f"Stream file not found at {stream_path}")
        print("Generating synthetic stream...")
        os.chdir(os.path.join(project_root, "data"))
        from generate_stream import generate_synthetic_stream
        generate_synthetic_stream()
        stream_path = os.path.join(project_root, "data", "stream.txt")
    
    # Run experiments
    results = run_experiment(stream_path, num_runs=5)
