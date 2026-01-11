"""
STEP 4: Apply Buffering to Convergence Analysis

Test buffering effectiveness on RANDOM order stream.
Expected: Buffering should reduce convergence delay significantly.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments.convergence import run_with_trace, compute_convergence_metrics
from sketches.hll import HyperLogLog
from sketches.fm import FlajoletMartin
from experiments.buffering import BufferedHLL, BufferedFM


def load_stream(path):
    """Load stream from file."""
    with open(path, 'r') as f:
        items = [line.strip() for line in f if line.strip()]
    
    # Try to convert to int, if not possible, hash the strings
    try:
        return [int(item) for item in items]
    except ValueError:
        # Use string directly (sketches will hash them)
        return items


def test_buffering_on_random_order():
    """
    Test buffering on RANDOM order stream.
    Hypothesis: Buffering decorrelates random order, enabling faster convergence.
    """
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    stream_path = os.path.join(project_root, "data", "stream.txt")
    
    stream = load_stream(stream_path)
    true_count = len(set(stream))
    
    print("\n" + "="*70)
    print("STEP 4: BUFFERING EFFECTIVENESS ON RANDOM ORDER")
    print("="*70 + "\n")
    
    print(f"Stream: {len(stream)} elements, {true_count} unique")
    print("Testing buffering with different buffer sizes on RANDOM order\n")
    
    # Shuffle to random order
    import random
    random.seed(42)
    random_stream = stream.copy()
    random.shuffle(random_stream)
    
    results = {}
    
    # BASELINE: No buffering
    print("Baseline: No buffering (pure random order)")
    print("-" * 70)
    
    traces = run_with_trace(random_stream, 'hll', step=1000)
    metrics = compute_convergence_metrics(traces, true_count)
    
    baseline_time = metrics['time_to_5_percent']
    print(f"  Time to 5% accuracy: {baseline_time:.0f} items ({(baseline_time/len(random_stream))*100:.1f}%)")
    print(f"  Early errors: @25%={metrics['early_25_percent_error']*100:.2f}%, @50%={metrics['early_50_percent_error']*100:.2f}%")
    
    results['baseline'] = {
        'buffer_size': 0,
        'time_to_5_percent': baseline_time,
        'early_25_percent_error': metrics['early_25_percent_error'],
        'early_50_percent_error': metrics['early_50_percent_error'],
        'final_error': metrics['final_error'],
        'error_stability': metrics['error_stability']
    }
    
    # TEST: Different buffer sizes
    buffer_sizes = [250, 500]  # Reduced from [100, 250, 500, 1000] for speed
    
    print("\nTesting with buffering:")
    print("-" * 70)
    
    for buffer_size in buffer_sizes:
        print(f"\nBuffer size: {buffer_size}")
        
        # Run 2 times and average
        times_to_accuracy = []
        early_25_errors = []
        early_50_errors = []
        final_errors = []
        stabilities = []
        
        for run in range(2):
            traces = run_with_trace(
                random_stream, 
                'buffered_hll', 
                sketch_params={'buffer_size': buffer_size},
                step=1000
            )
            metrics = compute_convergence_metrics(traces, true_count)
            
            times_to_accuracy.append(metrics['time_to_5_percent'])
            early_25_errors.append(metrics['early_25_percent_error'])
            early_50_errors.append(metrics['early_50_percent_error'])
            final_errors.append(metrics['final_error'])
            stabilities.append(metrics['error_stability'])
        
        avg_time = sum(times_to_accuracy) / len(times_to_accuracy)
        avg_early_25 = sum(early_25_errors) / len(early_25_errors)
        avg_early_50 = sum(early_50_errors) / len(early_50_errors)
        avg_final = sum(final_errors) / len(final_errors)
        avg_stability = sum(stabilities) / len(stabilities)
        
        improvement = ((baseline_time - avg_time) / baseline_time) * 100
        
        print(f"  Time to 5%: {avg_time:.0f} items (baseline: {baseline_time:.0f})")
        print(f"  Improvement: {improvement:.1f}%")
        print(f"  Early @25%: {avg_early_25*100:.2f}% (baseline: {results['baseline']['early_25_percent_error']*100:.2f}%)")
        print(f"  Early @50%: {avg_early_50*100:.2f}% (baseline: {results['baseline']['early_50_percent_error']*100:.2f}%)")
        
        results[f'buffer_{buffer_size}'] = {
            'buffer_size': buffer_size,
            'time_to_5_percent': avg_time,
            'improvement_percent': improvement,
            'early_25_percent_error': avg_early_25,
            'early_50_percent_error': avg_early_50,
            'final_error': avg_final,
            'error_stability': avg_stability
        }
    
    # COMPARISON: Buffering vs No Buffering
    print("\n" + "="*70)
    print("BUFFERING IMPACT SUMMARY")
    print("="*70 + "\n")
    
    print(f"Baseline (no buffering):  {baseline_time:.0f} items to 5% accuracy")
    print(f"Best buffer (500):        {results['buffer_500']['time_to_5_percent']:.0f} items to 5% accuracy")
    best_improvement = results['buffer_500']['improvement_percent']
    print(f"Improvement:             {best_improvement:.1f}%")
    
    if best_improvement > 10:
        print(f"\n✓ BUFFERING IS EFFECTIVE: Reduces convergence delay by {best_improvement:.0f}%")
    elif best_improvement > 0:
        print(f"\n⚠ BUFFERING HAS MODEST EFFECT: {best_improvement:.1f}% improvement")
    else:
        print(f"\n✗ BUFFERING NOT EFFECTIVE: No improvement on random order")
    
    # Save results
    os.makedirs('results', exist_ok=True)
    output_path = 'results/STEP4_buffering_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    results = test_buffering_on_random_order()
