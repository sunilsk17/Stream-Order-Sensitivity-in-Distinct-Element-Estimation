"""
STEP 1: Convergence Behavior Analysis

Measure how estimates evolve as we process the stream.
This is critical for online analytics and real-world systems.

Key insight: Final estimates are order-invariant.
Intermediate estimates are NOT, and that's where order sensitivity matters.
"""

import sys
import os
import random
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sketches.hll import HyperLogLog
from sketches.fm import FlajoletMartin
from sketches.linear_counting import LinearCounting
from experiments.buffering import BufferedHLL, BufferedFM


def load_stream(filepath):
    """Load stream from file."""
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]


def run_with_trace(stream, sketch_type='hll', sketch_params=None, step=1000):
    """
    Run sketch and record estimates at regular intervals.
    
    Args:
        stream: List of items
        sketch_type: 'hll', 'fm', 'buffered_hll', 'buffered_fm'
        sketch_params: Dict of parameters
        step: Record estimate every N items
    
    Returns:
        List of (position, estimate) tuples
    """
    if sketch_params is None:
        sketch_params = {}
    
    # Initialize sketch
    if sketch_type == 'hll':
        sketch = HyperLogLog(p=sketch_params.get('p', 10))
    elif sketch_type == 'fm':
        sketch = FlajoletMartin(num_hashes=sketch_params.get('num_hashes', 64))
    elif sketch_type == 'linear_counting':
        sketch = LinearCounting(m=sketch_params.get('m', 16384))
    elif sketch_type == 'buffered_hll':
        sketch = BufferedHLL(
            p=sketch_params.get('p', 10),
            buffer_size=sketch_params.get('buffer_size', 500)
        )
    elif sketch_type == 'buffered_fm':
        sketch = BufferedFM(
            num_hashes=sketch_params.get('num_hashes', 64),
            buffer_size=sketch_params.get('buffer_size', 500)
        )
    else:
        raise ValueError(f"Unknown sketch type: {sketch_type}")
    
    estimates = []
    
    # Process stream
    for i, item in enumerate(stream, 1):
        sketch.add(item)
        if i % step == 0:
            est = sketch.count()
            estimates.append({
                'position': i,
                'fraction_processed': i / len(stream),
                'estimate': est
            })
    
    # Final estimate
    est = sketch.count()
    estimates.append({
        'position': len(stream),
        'fraction_processed': 1.0,
        'estimate': est
    })
    
    return estimates


def compute_convergence_metrics(estimates, true_count):
    """
    Compute convergence metrics from trace data.
    
    Returns:
        Dict with:
        - time_to_5_percent: Position where error < 5%
        - early_10_percent_error: Error at 10% of stream
        - early_25_percent_error: Error at 25% of stream
        - early_50_percent_error: Error at 50% of stream
        - final_error: Error at end of stream
        - convergence_smoothness: Variance of error over time
    """
    if not estimates:
        return {}
    
    # Compute errors for all estimates
    errors = []
    for est_data in estimates:
        est = est_data['estimate']
        rel_error = abs(est - true_count) / true_count
        errors.append(rel_error)
    
    metrics = {}
    
    # Time to accuracy (first position < 5%)
    time_to_5 = None
    for est_data, error in zip(estimates, errors):
        if error < 0.05:
            time_to_5 = est_data['position']
            break
    metrics['time_to_5_percent'] = time_to_5
    
    # Early-stage errors
    early_10_idx = int(len(estimates) * 0.1)
    early_25_idx = int(len(estimates) * 0.25)
    early_50_idx = int(len(estimates) * 0.50)
    
    metrics['early_10_percent_error'] = errors[early_10_idx] if early_10_idx < len(errors) else None
    metrics['early_25_percent_error'] = errors[early_25_idx] if early_25_idx < len(errors) else None
    metrics['early_50_percent_error'] = errors[early_50_idx] if early_50_idx < len(errors) else None
    metrics['final_error'] = errors[-1]
    
    # Stability (std dev of errors)
    if len(errors) > 1:
        mean_error = sum(errors) / len(errors)
        variance = sum((e - mean_error) ** 2 for e in errors) / len(errors)
        metrics['error_stability'] = variance ** 0.5
    else:
        metrics['error_stability'] = 0
    
    return metrics


def run_convergence_experiment(stream_path, num_runs=3):
    """
    Run complete convergence experiment across all stream orders.
    """
    stream = load_stream(stream_path)
    true_count = len(set(stream))
    
    print("\n" + "="*70)
    print("STEP 1: CONVERGENCE BEHAVIOR ANALYSIS")
    print("="*70)
    print(f"Stream size: {len(stream)} elements")
    print(f"True cardinality: {true_count} unique elements")
    print(f"Runs per variant: {num_runs}")
    print("="*70 + "\n")
    
    # Generate stream orders
    orders = {}
    orders['original'] = stream[:]
    
    shuffled = stream[:]
    random.shuffle(shuffled)
    orders['random'] = shuffled
    
    # Chunk-shuffled
    chunked = []
    chunk_size = 1000
    for i in range(0, len(stream), chunk_size):
        chunk = stream[i:i + chunk_size]
        random.shuffle(chunk)
        chunked.extend(chunk)
    orders['chunk_shuffled'] = chunked
    
    # Grouped (sorted) order
    grouped = sorted(stream)
    orders['grouped'] = grouped
    
    # Store all results
    all_results = {}
    
    for order_name, ordered_stream in orders.items():
        print(f"\n{'='*70}")
        print(f"ORDER: {order_name.upper()}")
        print(f"{'='*70}\n")
        
        order_results = {}
        
        # HyperLogLog convergence
        print(f"HyperLogLog convergence (p=10):")
        hll_traces = []
        hll_metrics_list = []
        
        for run in range(num_runs):
            trace = run_with_trace(ordered_stream, 'hll', {'p': 10}, step=1000)
            hll_traces.append(trace)
            metrics = compute_convergence_metrics(trace, true_count)
            hll_metrics_list.append(metrics)
        
        # Average metrics across runs
        hll_avg_metrics = {}
        for key in hll_metrics_list[0].keys():
            values = [m[key] for m in hll_metrics_list if m[key] is not None]
            if values:
                hll_avg_metrics[key] = sum(values) / len(values)
        
        print(f"  Time to 5% accuracy:     {hll_avg_metrics.get('time_to_5_percent', 'N/A')} items")
        print(f"  Error @ 10% of stream:   {hll_avg_metrics.get('early_10_percent_error', 'N/A')*100:.2f}%")
        print(f"  Error @ 25% of stream:   {hll_avg_metrics.get('early_25_percent_error', 'N/A')*100:.2f}%")
        print(f"  Error @ 50% of stream:   {hll_avg_metrics.get('early_50_percent_error', 'N/A')*100:.2f}%")
        print(f"  Final error:             {hll_avg_metrics.get('final_error', 'N/A')*100:.2f}%")
        print(f"  Error stability (σ):     {hll_avg_metrics.get('error_stability', 'N/A')*100:.4f}%")
        
        order_results['hll'] = {
            'traces': hll_traces,
            'metrics': hll_avg_metrics
        }
        
        # Flajolet-Martin convergence
        print(f"\nFlajolet-Martin convergence (64 hashes):")
        fm_traces = []
        fm_metrics_list = []
        
        for run in range(num_runs):
            trace = run_with_trace(ordered_stream, 'fm', {'num_hashes': 64}, step=1000)
            fm_traces.append(trace)
            metrics = compute_convergence_metrics(trace, true_count)
            fm_metrics_list.append(metrics)
        
        fm_avg_metrics = {}
        for key in fm_metrics_list[0].keys():
            values = [m[key] for m in fm_metrics_list if m[key] is not None]
            if values:
                fm_avg_metrics[key] = sum(values) / len(values)
        
        print(f"  Time to 5% accuracy:     {fm_avg_metrics.get('time_to_5_percent', 'N/A')} items")
        print(f"  Error @ 10% of stream:   {fm_avg_metrics.get('early_10_percent_error', 'N/A')*100:.2f}%")
        print(f"  Error @ 25% of stream:   {fm_avg_metrics.get('early_25_percent_error', 'N/A')*100:.2f}%")
        print(f"  Error @ 50% of stream:   {fm_avg_metrics.get('early_50_percent_error', 'N/A')*100:.2f}%")
        print(f"  Final error:             {fm_avg_metrics.get('final_error', 'N/A')*100:.2f}%")
        print(f"  Error stability (σ):     {fm_avg_metrics.get('error_stability', 'N/A')*100:.4f}%")
        
        order_results['fm'] = {
            'traces': fm_traces,
            'metrics': fm_avg_metrics
        }
        
        all_results[order_name] = order_results
    
    # Test buffered HLL on grouped order
    print(f"\n{'='*70}")
    print(f"BUFFERED HLL ON GROUPED ORDER (buffer_size=500)")
    print(f"{'='*70}\n")
    
    grouped_stream = orders['grouped']
    buffered_traces = []
    buffered_metrics_list = []
    
    for run in range(num_runs):
        trace = run_with_trace(
            grouped_stream,
            'buffered_hll',
            {'p': 10, 'buffer_size': 500},
            step=1000
        )
        buffered_traces.append(trace)
        metrics = compute_convergence_metrics(trace, true_count)
        buffered_metrics_list.append(metrics)
    
    buffered_avg_metrics = {}
    for key in buffered_metrics_list[0].keys():
        values = [m[key] for m in buffered_metrics_list if m[key] is not None]
        if values:
            buffered_avg_metrics[key] = sum(values) / len(values)
    
    print(f"  Time to 5% accuracy:     {buffered_avg_metrics.get('time_to_5_percent', 'N/A')} items")
    print(f"  Error @ 10% of stream:   {buffered_avg_metrics.get('early_10_percent_error', 'N/A')*100:.2f}%")
    print(f"  Error @ 25% of stream:   {buffered_avg_metrics.get('early_25_percent_error', 'N/A')*100:.2f}%")
    print(f"  Error @ 50% of stream:   {buffered_avg_metrics.get('early_50_percent_error', 'N/A')*100:.2f}%")
    print(f"  Final error:             {buffered_avg_metrics.get('final_error', 'N/A')*100:.2f}%")
    print(f"  Error stability (σ):     {buffered_avg_metrics.get('error_stability', 'N/A')*100:.4f}%")
    
    all_results['buffered_grouped'] = {
        'traces': buffered_traces,
        'metrics': buffered_avg_metrics
    }
    
    # Summary comparison
    print(f"\n{'='*70}")
    print("CONVERGENCE SUMMARY: Time to 5% Accuracy")
    print(f"{'='*70}\n")
    
    for order in ['original', 'random', 'grouped']:
        hll_time = all_results[order]['hll']['metrics'].get('time_to_5_percent', 'N/A')
        print(f"{order:15s} HLL: {hll_time} items")
    
    print(f"\n{'Buffered (grouped)':15s} HLL: {all_results['buffered_grouped']['metrics'].get('time_to_5_percent', 'N/A')} items")
    
    print(f"\n{'='*70}")
    print("Improvement ratio (grouped/buffered grouped):")
    grouped_time = all_results['grouped']['hll']['metrics'].get('time_to_5_percent')
    buffered_time = all_results['buffered_grouped']['metrics'].get('time_to_5_percent')
    if grouped_time and buffered_time and buffered_time > 0:
        ratio = grouped_time / buffered_time
        print(f"Buffering provides {ratio:.2f}× faster convergence on grouped data")
    print(f"{'='*70}\n")
    
    return all_results


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    stream_path = os.path.join(project_root, "data", "stream.txt")
    
    if not os.path.exists(stream_path):
        print(f"Stream file not found. Generating synthetic stream...")
        os.chdir(os.path.join(project_root, "data"))
        from generate_stream import generate_synthetic_stream
        generate_synthetic_stream()
        stream_path = os.path.join(project_root, "data", "stream.txt")
    
    results = run_convergence_experiment(stream_path, num_runs=3)
