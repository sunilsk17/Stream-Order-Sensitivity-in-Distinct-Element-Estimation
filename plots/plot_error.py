"""
Visualization of experimental results.

Plots the effect of stream order on sketch accuracy.
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments.run_orders import run_experiment
from experiments.buffering import compare_buffering_strategies


def plot_order_sensitivity(results):
    """
    Plot mean relative errors across different stream orders.
    
    Args:
        results: Dictionary from run_experiment()
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    order_names = list(results.keys())
    
    # HLL errors
    hll_errors = [results[order]['hll']['mean_error'] * 100 for order in order_names]
    fm_errors = [results[order]['fm']['mean_error'] * 100 for order in order_names]
    
    x = np.arange(len(order_names))
    width = 0.35
    
    axes[0].bar(x - width/2, hll_errors, width, label='HyperLogLog', color='steelblue')
    axes[0].bar(x + width/2, fm_errors, width, label='Flajolet-Martin', color='coral')
    axes[0].set_xlabel('Stream Order Type')
    axes[0].set_ylabel('Mean Relative Error (%)')
    axes[0].set_title('Effect of Stream Order on Sketch Accuracy')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(order_names, rotation=15, ha='right')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)
    
    # Error variance (stability)
    hll_stdev = [results[order]['hll']['stdev'] * 100 for order in order_names]
    fm_stdev = [results[order]['fm']['stdev'] * 100 for order in order_names]
    
    axes[1].bar(x - width/2, hll_stdev, width, label='HyperLogLog', color='steelblue')
    axes[1].bar(x + width/2, fm_stdev, width, label='Flajolet-Martin', color='coral')
    axes[1].set_xlabel('Stream Order Type')
    axes[1].set_ylabel('Error Standard Deviation (%)')
    axes[1].set_title('Estimation Stability Across Orders')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(order_names, rotation=15, ha='right')
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), 'order_sensitivity.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to: {output_path}")
    plt.close()


def plot_buffering_improvement(buffering_results):
    """
    Plot buffering improvement across different buffer sizes.
    
    Args:
        buffering_results: Dictionary from compare_buffering_strategies()
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    buffer_sizes = list(buffering_results.keys())
    
    # HLL improvements
    hll_standard = [buffering_results[b]['hll']['mean_error'] * 100 for b in buffer_sizes]
    hll_buffered = [buffering_results[b]['buffered_hll']['mean_error'] * 100 for b in buffer_sizes]
    
    fm_standard = [buffering_results[b]['fm']['mean_error'] * 100 for b in buffer_sizes]
    fm_buffered = [buffering_results[b]['buffered_fm']['mean_error'] * 100 for b in buffer_sizes]
    
    x = np.arange(len(buffer_sizes))
    width = 0.35
    
    axes[0].plot(x, hll_standard, marker='o', linewidth=2, markersize=8, 
                 label='HLL (Standard)', color='steelblue')
    axes[0].plot(x, hll_buffered, marker='s', linewidth=2, markersize=8, 
                 label='HLL (Buffered)', color='darkblue', linestyle='--')
    axes[0].set_xlabel('Buffer Size (items)')
    axes[0].set_ylabel('Mean Relative Error (%)')
    axes[0].set_title('HyperLogLog: Buffering Effect')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(buffer_sizes)
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    axes[1].plot(x, fm_standard, marker='o', linewidth=2, markersize=8, 
                 label='FM (Standard)', color='coral')
    axes[1].plot(x, fm_buffered, marker='s', linewidth=2, markersize=8, 
                 label='FM (Buffered)', color='darkred', linestyle='--')
    axes[1].set_xlabel('Buffer Size (items)')
    axes[1].set_ylabel('Mean Relative Error (%)')
    axes[1].set_title('Flajolet-Martin: Buffering Effect')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(buffer_sizes)
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), 'buffering_improvement.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to: {output_path}")
    plt.close()


if __name__ == "__main__":
    print("Generating plots...")
    print("\n" + "="*70)
    print("GENERATING ORDER SENSITIVITY PLOT")
    print("="*70 + "\n")
    
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
    
    # Run order sensitivity experiment
    results = run_experiment(stream_path, num_runs=5)
    plot_order_sensitivity(results)
    
    print("\n" + "="*70)
    print("GENERATING BUFFERING IMPROVEMENT PLOT")
    print("="*70 + "\n")
    
    # Run buffering experiment
    buffering_results = compare_buffering_strategies(stream_path, num_runs=5)
    plot_buffering_improvement(buffering_results)
    
    print("\nAll plots generated successfully!")
