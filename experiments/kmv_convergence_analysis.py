#!/usr/bin/env python3
"""
KMV (K-Minimum Values) Cardinality Analysis - Real Public Datasets

Analyzes order sensitivity of KMV algorithm on the same
publicly available datasets used for HLL analysis:
1. Wikipedia pageviews (public archive logs)
2. GitHub events (public archive)
3. Common Crawl (public crawl of web)
4. Enron email corpus (public corpus)

Follows identical methodology to HLL analysis for direct comparison.
"""

import json
import math
from pathlib import Path
from datetime import datetime

# Import KMV implementation
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from sketches.kmv import KMVSketch


def load_stream_from_file(filepath, limit=None):
    """
    Load stream from file.
    
    Args:
        filepath: Path to stream file
        limit: Maximum items to load (None = all)
    
    Returns:
        List of items
    """
    items = []
    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            items.append(line.strip())
    return items


def analyze_convergence(items, dataset_name, ordering_name, k=512):
    """
    Run convergence test with KMV Sketch.
    
    Args:
        items: Stream of items
        dataset_name: Name of dataset
        ordering_name: Type of ordering (grouped/random/chrono)
        k: Number of minimum values to keep
    
    Returns:
        Dictionary with convergence results
    """
    sketch = KMVSketch(k=k)
    convergence = []
    checkpoint_interval = max(1, len(items) // 20)  # 20 checkpoints
    
    true_unique = len(set(items))
    time_to_5pct = len(items)
    final_error = 0
    
    for i, item in enumerate(items):
        sketch.add(item)
        
        # Check at intervals
        if (i + 1) % checkpoint_interval == 0 or i == len(items) - 1:
            estimate = sketch.cardinality()
            if estimate < 1:
                estimate = 1
            
            error = abs(estimate - true_unique) / true_unique * 100
            pct = 100 * (i + 1) / len(items)
            
            convergence.append({
                'items': i + 1,
                'pct': round(pct, 1),
                'estimate': round(estimate),
                'error': round(error, 2)
            })
            
            # Track time to 5% error
            if error <= 5.0 and time_to_5pct == len(items):
                time_to_5pct = i + 1
            
            final_error = error
    
    return {
        'dataset': dataset_name,
        'ordering': ordering_name,
        'items_total': len(items),
        'unique_true': true_unique,
        'unique_pct': round(100 * true_unique / len(items), 1),
        'time_to_5pct_error': time_to_5pct,
        'final_error': round(final_error, 2),
        'convergence': convergence,
        'sketch_parameter_k': k
    }


def main():
    """Run KMV analysis on all datasets."""
    print("=" * 80)
    print("KMV (K-MINIMUM VALUES) CARDINALITY ANALYSIS - REAL PUBLIC DATASETS")
    print("=" * 80)
    print()
    print("Algorithm: KMV (K-Minimum Values)")
    print("Sketch Parameter: k = 512 (comparable to HLL p=10)")
    print()
    
    datasets = {
        'Wikipedia': {
            'grouped': 'data/wikipedia_items_grouped.txt',
            'random': 'data/wikipedia_items_random.txt',
            'chrono': 'data/wikipedia_items_chrono.txt',
        },
        'GitHub': {
            'grouped': 'data/github_items_grouped.txt',
            'random': 'data/github_items_random.txt',
            'chrono': 'data/github_items_chrono.txt',
        },
        'Common Crawl': {
            'grouped': 'data/commoncrawl_items_grouped.txt',
            'random': 'data/commoncrawl_items_random.txt',
            'chrono': 'data/commoncrawl_items_chrono.txt',
        },
        'Enron': {
            'grouped': 'data/enron_items_grouped.txt',
            'random': 'data/enron_items_random.txt',
            'chrono': 'data/enron_items_chrono.txt',
        }
    }
    
    # Load all datasets first
    print("LOADING DATASETS (REAL PUBLIC DATA ONLY)...")
    print("-" * 80)
    
    loaded_datasets = {}
    for dataset_name, files in datasets.items():
        print(f"\n{dataset_name}:")
        
        # Load grouped variant to get stats
        items = load_stream_from_file(files['grouped'])
        unique = len(set(items))
        dup_ratio = 100 * (len(items) - unique) / len(items)
        
        loaded_datasets[dataset_name] = {
            'files': files,
            'total': len(items),
            'unique': unique,
            'dup_ratio': dup_ratio
        }
        
        print(f"  Total items: {len(items):,}")
        print(f"  Unique items: {unique:,}")
        print(f"  Duplicate ratio: {dup_ratio:.1f}%")
    
    # Run experiments
    print("\n" + "=" * 80)
    print("RUNNING CONVERGENCE TESTS (3 ORDERINGS × 4 DATASETS = 12 EXPERIMENTS)")
    print("=" * 80)
    
    all_results = []
    sensitivity_summary = []
    
    for dataset_name, dataset_info in loaded_datasets.items():
        print(f"\nDataset: {dataset_name}")
        print("-" * 80)
        
        times = {}
        
        for ordering_name in ['grouped', 'random', 'chrono']:
            filepath = dataset_info['files'][ordering_name]
            print(f"  Testing {ordering_name} order... ", end='', flush=True)
            
            items = load_stream_from_file(filepath)
            result = analyze_convergence(items, dataset_name, ordering_name, k=512)
            all_results.append(result)
            times[ordering_name] = result['time_to_5pct_error']
            
            print(f"✓ {result['time_to_5pct_error']:,} items to 5% error")
        
        # Calculate sensitivity
        grouped_time = times['grouped']
        random_time = times['random']
        sensitivity = grouped_time / random_time if random_time > 0 else 1.0
        
        print(f"\n  Sensitivity factor: {sensitivity:.3f}×")
        print(f"    (Grouped: {grouped_time:,} items vs Random: {random_time:,} items)")
        
        sensitivity_summary.append({
            'dataset': dataset_name,
            'unique': dataset_info['unique'],
            'dup_pct': dataset_info['dup_ratio'],
            'sensitivity': round(sensitivity, 3)
        })
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'algorithm': 'KMV (K-Minimum Values)',
        'sketch_parameter_k': 512,
        'note': 'All datasets are REAL PUBLIC DATA - NO synthetic elements. Parallel analysis with HLL for comparison.',
        'datasets_info': {
            row['dataset']: {
                'total': loaded_datasets[row['dataset']]['total'],
                'unique': loaded_datasets[row['dataset']]['unique'],
                'duplicate_ratio': round(loaded_datasets[row['dataset']]['dup_ratio'], 1),
                'source': 'Public archive' if row['dataset'] != 'Common Crawl' 
                         else 'Common Crawl (https://commoncrawl.org/)'
            }
            for row in sensitivity_summary
        },
        'experiments': all_results,
        'sensitivity_summary': sensitivity_summary
    }
    
    output_path = Path('results/kmv_convergence_analysis_results.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 80)
    print("SENSITIVITY SPECTRUM SUMMARY - KMV")
    print("=" * 80)
    print(f"{'Dataset':<15} {'Unique':<10} {'Dup%':<8} {'Sensitivity':<12}")
    print("-" * 80)
    
    for row in sorted(sensitivity_summary, key=lambda x: x['dup_pct']):
        print(f"{row['dataset']:<15} {row['unique']:<10,d} {row['dup_pct']:<8.1f} {row['sensitivity']:<12.3f}×")
    
    print("\n" + "=" * 80)
    print("KEY FINDINGS - KMV")
    print("=" * 80)
    print("✓ All experiments use REAL PUBLIC datasets - NO synthetic data")
    print("✓ Same datasets as HLL analysis for direct comparison")
    print("✓ Sketch parameter k=512 (comparable to HLL p=10)")
    print("✓ Results show KMV order sensitivity patterns")
    print(f"✓ Results saved to: {output_path}")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
